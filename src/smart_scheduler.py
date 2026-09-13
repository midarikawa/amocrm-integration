from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math

class SmartScheduler:
    """Умный планировщик задач для специалистов"""

    def __init__(self, sheets_client, notion_client):
        self.sheets_client = sheets_client
        self.notion_client = notion_client

    def calculate_distance(self, addr1: str, addr2: str) -> float:
        """
        Вычисление расстояния между адресами
        В будущем можно интегрировать Google Maps API
        Пока используем простую эвристику км/балл
        """
        if not addr1 or not addr2:
            return 100.0

        addr1_lower = addr1.lower()
        addr2_lower = addr2.lower()

        #Простая эвристика: ищем общие слова в адресах - чем больше общих слов
        keywords1 = set(addr1_lower.split())
        keywords2 = set(addr2_lower.split())

        common = keywords1.intersection(keywords2)

        if len(common) >= 2:
            return 5.0  # Близко
        elif len(common) == 1:
            return 20.0  # Средне
        else:
            return 50.0  # Далеко

    def get_specialist_schedule(self, specialist_id: int, date: str) -> List[Dict]:
        """Получить расписание специалиста на дату"""
        #Получаем расписание из Google Sheets
        schedule = self.sheets_client.get_specialist_schedule(specialist_id, date)
        return schedule if schedule else []

    def calculate_workload(self, specialist_id: int, date: str) -> int:
        """Вычислить загруженность специалиста на дату (в минутах)"""
        schedule = self.get_specialist_schedule(specialist_id, date)
        total_minutes = sum(task.get('work_time', 60) for task in schedule)
        return total_minutes

    def is_time_slot_available(self, specialist_id: int, date: str, time: str, duration: int) -> bool:
        """Проверить, свободен ли временной слот у специалиста"""
        schedule = self.get_specialist_schedule(specialist_id, date)

        if not schedule:
            return True

        try:
            new_start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            new_end = new_start + timedelta(minutes=duration)

            for task in schedule:
                task_start = datetime.strptime(f"{task['date']} {task['time']}", "%Y-%m-%d %H:%M")
                task_end = task_start + timedelta(minutes=task.get('work_time', 60))

                #Проверяем пересечение интервалов
                if (new_start < task_end) and (new_end > task_start):
                    return False

            return True
        except:
            return True

    def calculate_specialist_score(self, specialist: Dict, task_data: Dict) -> float:
        """
        Вычислить оценку подходящести специалиста для задачи
        Чем выше оценка, тем лучше подходит
        """
        score = 100.0

        specialist_id = specialist.get('ID')
        work_type = task_data.get('work_type', '')
        specialization = specialist.get('Специализация', '')
        date = task_data.get('visit_date')
        time = task_data.get('visit_time', '10:00')
        duration = task_data.get('work_time', 60)
        address = task_data.get('address', '')

        # 1. Соответствие специализации (вес: 30 баллов)
        if work_type and specialization:
            if work_type.lower() in specialization.lower():
                score += 30
            else:
                score -= 10

        # 2. Доступность временного слота (вес: 40 баллов)
        if not self.is_time_slot_available(specialist_id, date, time, duration):
            score -= 40  #Слот занят - большой штраф

        # 3. Загруженность на день (вес: 20 баллов)
        workload = self.calculate_workload(specialist_id, date)
        if workload == 0:
            score += 20  #Свободен полностью
        elif workload < 240:  #Меньше 4 часов
            score += 10
        elif workload > 480:  #Больше 8 часов
            score -= 20

        # 4. Близость к другим задачам в расписании (вес: 10 баллов)
        schedule = self.get_specialist_schedule(specialist_id, date)
        if schedule:
            #Ищем ближайшую задачу по адресу
            closest_distance = 100.0
            for task in schedule:
                distance = self.calculate_distance(address, task.get('address', ''))
                if distance < closest_distance:
                    closest_distance = distance

            if closest_distance < 10:
                score += 10
            elif closest_distance < 30:
                score += 5

        return score

    def find_best_specialist(self, task_data: Dict) -> Optional[Dict]:
        """Найти лучшего специалиста для задачи"""
        work_type = task_data.get('work_type', '')

        #Получаем всех активных специалистов
        specialists = self.sheets_client.get_active_specialists()

        if not specialists:
            return None

        #Фильтруем по специализации если указана
        if work_type:
            specialized = [s for s in specialists
                          if work_type.lower() in s.get('Специализация', '').lower()]
            if specialized:
                specialists = specialized

        #Вычисляем оценку для каждого
        scored_specialists = []
        for specialist in specialists:
            score = self.calculate_specialist_score(specialist, task_data)
            scored_specialists.append({
                'specialist': specialist,
                'score': score
            })

        #Сортируем по убыванию оценки
        scored_specialists.sort(key=lambda x: x['score'], reverse=True)

        #Возвращаем лучшего
        if scored_specialists:
            best = scored_specialists[0]
            print(f"Выбран специалист: {best['specialist'].get('Имя')} (оценка: {best['score']:.1f})")
            return best['specialist']

        return None

    def find_best_specialists(self, task_data: Dict, count: int) -> List[Dict]:
        """Найти несколько лучших специалистов для задачи"""
        work_type = task_data.get('work_type', '')

        specialists = self.sheets_client.get_active_specialists()

        if not specialists:
            return []

        #Фильтруем по специализации
        if work_type:
            specialized = [s for s in specialists
                          if work_type.lower() in s.get('Специализация', '').lower()]
            if specialized:
                specialists = specialized

        #Оцениваем каждого
        scored_specialists = []
        for specialist in specialists:
            score = self.calculate_specialist_score(specialist, task_data)
            scored_specialists.append({
                'specialist': specialist,
                'score': score
            })

        #Сортируем и берем топ N
        scored_specialists.sort(key=lambda x: x['score'], reverse=True)

        result = []
        for item in scored_specialists[:count]:
            if item['score'] > 0:  #Только с положительной оценкой
                result.append(item['specialist'])

        return result

    def optimize_daily_schedule(self, specialist_id: int, date: str) -> List[Dict]:
        """
        Оптимизировать расписание специалиста на день
        Используем жадный алгоритм ближайшего соседа
        """
        schedule = self.get_specialist_schedule(specialist_id, date)

        if not schedule or len(schedule) <= 1:
            return schedule

        #Алгоритм: начинаем с первой задачи (по времени)
        #Затем каждый раз выбираем ближайшую по адресу
        optimized = []
        remaining = schedule.copy()

        #Берем первую задачу
        current = remaining.pop(0)
        optimized.append(current)

        #Жадно выбираем: каждый раз ближайшую
        while remaining:
            current_addr = current.get('address', '')

            #Ищем ближайшую задачу
            min_distance = float('inf')
            nearest_idx = 0

            for idx, task in enumerate(remaining):
                distance = self.calculate_distance(current_addr, task.get('address', ''))
                if distance < min_distance:
                    min_distance = distance
                    nearest_idx = idx

            current = remaining.pop(nearest_idx)
            optimized.append(current)

        return optimized
