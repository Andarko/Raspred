from random import Random
import sys
# This is a sample Python script.


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
class Main:
    def __init__(self):
        # Задачи
        self.count_tasks = 20
        self.tasks = list()
        # self.task_middle_score = list()
        r = Random()
        for i in range(self.count_tasks):
            new_task = Task()
            new_task.index = i
            new_task.middle_score = int(r.random() * r.random() * r.random() * 200 + 10)
            # print("middle = " + str(new_task.middle_score))
            self.tasks.append(new_task)

        # Работники
        self.count_workers = 5
        self.workers = list()
        work_norm_sum = 0
        for i in range(self.count_workers):
            new_worker = Worker()
            new_worker.index = i
            # Всем для начала одинаковое количество работы на выработку
            new_worker.work_norm = 100
            # if i == 0:
            #     new_worker.work_norm = 40
            work_norm_sum += new_worker.work_norm
            sum_scores = 0
            for task in self.tasks:
                score = task.middle_score
                for j in range(3):
                    score *= (1 + r.random())
                    score /= (1 + r.random())

                new_worker.scores.append(int(score))
                sum_scores += int(score)

            for score in new_worker.scores:
                new_worker.scores_norm.append(score / sum_scores)

            self.workers.append(new_worker)

        # Определение лимита работы для каждого
        for worker in self.workers:
            worker.work_limit = worker.work_norm / work_norm_sum
        # Лимит работы уменьшаем в сторону минимальных оценок
        min_scores_sum = 0
        for task in self.tasks:
            task.min_score = sys.float_info.max
            for worker in self.workers:
                if task.min_score > worker.scores_norm[task.index]:
                    task.min_score = worker.scores_norm[task.index]

            min_scores_sum += task.min_score
        # Берем пределом работ среднее между средним лимитом и лимитом минимальной оценки
        reduction_rate = min_scores_sum + 0.5 * (1 - min_scores_sum)
        for worker in self.workers:
            worker.work_limit *= reduction_rate
            print("Worker " + str(worker.index) + "(lim=" + str(round(worker.work_limit, 3)) + ") score "
                  + str(worker.scores_norm))

        print("inited")

    # Функция, распределяющая задачи по сотрудникам целыми
    def distribute_soft(self, overwork_rate=0.4):
        for task in self.tasks:
            # task.min_score = 1
            task.need_take = True
            task.free = True
            task.worker = None
        for worker in self.workers:
            worker.need_work = True
            worker.free = True
            worker.tasks = list()
            worker.task_scores_sum = 0.0
        print("rate=" + str(overwork_rate))
        # overwork_rate - насколько учитывать переработку в оценке задач
        free_workers_count = self.count_workers
        free_tasks_count = self.count_tasks
        undistributed = 0
        work_norm_sum = 0
        # Максимальный лимит работы среди работников
        max_work_limit = 0
        for worker in self.workers:
            if max_work_limit < worker.work_limit:
                max_work_limit = worker.work_limit
            work_norm_sum += worker.work_norm
            for i in range(self.count_tasks):
                undistributed += worker.scores_norm[i]

        while free_tasks_count and free_workers_count:
            # Ищем самого незагруженого работника
            lazy_worker_score = sys.float_info.max
            for worker in self.workers:
                if worker.free:
                    if lazy_worker_score > worker.task_scores_sum:
                        lazy_worker_score = worker.task_scores_sum

            for task in self.tasks:
                if task.free:
                    task.need_take = True

            # Ищем наибольший перекос
            max_delta = -1
            max_delta_index = -1
            for i in range(self.count_tasks):
                if self.tasks[i].free and self.tasks[i].need_take:
                    task_workers_list = list()
                    min_score = sys.float_info.max
                    min_worker = None
                    avg_score = 0.0
                    # Хорошо было бы оценивать не по average, а как-то сложнее ???
                    count = 0
                    for worker in self.workers:
                        if worker.free:
                            task_workers_list.append((worker, worker.scores_norm[i]))
                            # if max_score < worker.scores_norm[i]:
                            #     max_score = worker.scores_norm[i]
                            avg_score += worker.scores_norm[i]
                            count += 1
                            if min_score > worker.scores_norm[i]:
                                min_score = worker.scores_norm[i]
                                min_worker = worker
                    avg_score /= count
                    score_delta = 0.0
                    rate = 1.0
                    task_workers_sorted_list = sorted(task_workers_list, key=lambda work: work[1])

                    for worker_score in task_workers_sorted_list:
                        if worker_score[1] >= min_score:
                            score_delta += (worker_score[1] + worker_score[0].task_scores_sum * overwork_rate
                                            - min_score - min_worker.task_scores_sum * overwork_rate) \
                                           * rate
                            rate /= 2

                    # if max_delta < avg_score - min_score:
                    if max_delta < score_delta:
                        # max_delta = avg_score - min_score
                        max_delta = score_delta
                        max_delta_index = i

            min_score = sys.float_info.max
            for worker in self.workers:
                if worker.free:
                    if min_score > worker.scores_norm[max_delta_index] + worker.task_scores_sum * overwork_rate:
                        min_score = worker.scores_norm[max_delta_index] + worker.task_scores_sum * overwork_rate
                        worker_min_score = worker

            # Присвоение задачи
            print(str(worker_min_score.index) + "<=" + str(max_delta_index) + ": "
                  + str(round(worker_min_score.scores_norm[max_delta_index], 3))
                  + "(+" + str(round(worker_min_score.scores_norm[max_delta_index]
                                     - self.tasks[max_delta_index].min_score, 3)) + ")")

            self.tasks[max_delta_index].free = False
            self.tasks[max_delta_index].need_take = False
            self.tasks[max_delta_index].worker = worker_min_score
            worker_min_score.tasks.append(self.tasks[max_delta_index])
            worker_min_score.task_scores_sum += worker_min_score.scores_norm[max_delta_index]
            if worker_min_score.task_scores_sum > worker_min_score.work_limit:
                worker_min_score.free = False
                # print("Worker limit " + str(worker_min_score.index))
            free_tasks_count -= 1

        print("distributed!")
        for worker in self.workers:
            tasks_list = list()
            for task in worker.tasks:
                tasks_list.append(task.index)
            print("Worker " + str(worker.index) + ": " + str(round(worker.task_scores_sum, 3))
                  + "\t" + str(tasks_list))

    # Функция, распределяющая задачи по сотрудникам целыми
    def distribute(self):
        # Коэффициент, определяющий насколько загруженность работника должна превышить минимальную среди всех
        # чтобы ему не участвовать в следующем конкурсе распределения работ
        worker_engagement_rate = 0.15

        free_workers_count = self.count_workers
        free_tasks_count = self.count_tasks
        undistributed = 0
        work_norm_sum = 0
        # Максимальный лимит работы среди работников
        max_work_limit = 0
        for worker in self.workers:
            if max_work_limit < worker.work_limit:
                max_work_limit = worker.work_limit
            work_norm_sum += worker.work_norm
            for i in range(self.count_tasks):
                undistributed += worker.scores_norm[i]

        while free_tasks_count and free_workers_count:
            # Ищем самого незагруженого работника
            lazy_worker_score = sys.float_info.max
            for worker in self.workers:
                if worker.free:
                    if lazy_worker_score > worker.task_scores_sum:
                        lazy_worker_score = worker.task_scores_sum

            # Помечаем работников, которым положено взять работу
            for worker in self.workers:
                if worker.free:
                    worker.need_work = worker.task_scores_sum \
                                       <= lazy_worker_score + worker_engagement_rate * worker.work_limit

            # # Коэффициент определяет насколько работа должна быть оценена меньше максимальной
            # # чтобы ее рассматривать в работу
            # task_engagement_rate = 0.7
            # # Коэффициент, определяющий - какой относительно рабочего лимита должна быть оценка задачи
            # # чтобы проводить конкурс задач на рассмотрение их в работу
            # big_task_rate = 1.0
            # # Ищем самую тяжелооцененную работу
            # harder_task_score = 0
            # for task in self.tasks:
            #     if task.free:
            #         min_task_score = sys.float_info.max
            #         for worker in self.workers:
            #             if worker.free:
            #                 if min_task_score > worker.scores_norm[task.index]:
            #                     min_task_score = worker.scores_norm[task.index]
            #         if harder_task_score < min_task_score:
            #             harder_task_score = min_task_score

            # # Помечаем - какие работы нужно разобрать сейчас
            # if harder_task_score >= big_task_rate * max_work_limit:
            #     print("hard task!")
            #     for task in self.tasks:
            #         if task.free:
            #             min_task_score = sys.float_info.max
            #             for worker in self.workers:
            #                 if worker.free:
            #                     if min_task_score > worker.scores_norm[task.index]:
            #                         min_task_score = worker.scores_norm[task.index]
            #             task.need_take = min_task_score >= task_engagement_rate * harder_task_score
            # else:
            for task in self.tasks:
                if task.free:
                    task.need_take = True

            # Ищем наибольший перекос
            max_delta = -1
            max_delta_index = -1
            for i in range(self.count_tasks):
                if self.tasks[i].free and self.tasks[i].need_take:
                    task_scores_list = list()
                    min_score = sys.float_info.max
                    avg_score = 0.0
                    # Хорошо было бы оценивать не по average, а как-то сложнее ???
                    count = 0
                    for worker in self.workers:
                        if worker.free:
                            task_scores_list.append(worker.scores_norm[i])
                            # if max_score < worker.scores_norm[i]:
                            #     max_score = worker.scores_norm[i]
                            avg_score += worker.scores_norm[i]
                            count += 1
                            if worker.need_work and min_score > worker.scores_norm[i]:
                                min_score = worker.scores_norm[i]
                    avg_score /= count
                    score_delta = 0.0
                    rate = 1.0
                    task_scores_list.sort()
                    for score in task_scores_list:
                        if score >= min_score:
                            score_delta += (score - min_score) * rate
                            rate /= 2

                    # if max_delta < avg_score - min_score:
                    if max_delta < score_delta:
                        # max_delta = avg_score - min_score
                        max_delta = score_delta
                        max_delta_index = i

            # min_score = sys.float_info.max
            # for worker in self.workers:
            #     if worker.need_work:
            #         if min_score > worker.scores_norm[max_delta_index]:
            #             min_score = worker.scores_norm[max_delta_index]
            #             worker_min_score = worker
            min_score = sys.float_info.max
            # if not worker_min_score.free:
            #     print("Worker " + str(worker_min_score.index) + " не получил работу " + str(max_delta_index))
            for worker in self.workers:
                if worker.free and worker.need_work:
                    if min_score > worker.scores_norm[max_delta_index]:
                        min_score = worker.scores_norm[max_delta_index]
                        worker_min_score = worker

            # Присвоение задачи
            print(str(worker_min_score.index) + "<=" + str(max_delta_index) + ": "
                  + str(round(worker_min_score.scores_norm[max_delta_index], 3))
                  + "(+" + str(round(worker_min_score.scores_norm[max_delta_index]
                                     - self.tasks[max_delta_index].min_score, 3)) + ")")

            self.tasks[max_delta_index].free = False
            self.tasks[max_delta_index].need_take = False
            worker_min_score.tasks.append(self.tasks[max_delta_index])
            worker_min_score.task_scores_sum += worker_min_score.scores_norm[max_delta_index]
            if worker_min_score.task_scores_sum > worker_min_score.work_limit:
                worker_min_score.free = False
                worker_min_score.need_work = False
                # print("Worker limit " + str(worker_min_score.index))
            free_tasks_count -= 1

        print("distributed!")
        for worker in self.workers:
            tasks_list = list()
            for task in worker.tasks:
                tasks_list.append(task.index)
            print("Worker " + str(worker.index) + ": " + str(round(worker.task_scores_sum, 3))
                  + "\t" + str(tasks_list))


class Worker:
    def __init__(self):
        # Исходные данные
        self.index = -1
        self.scores = list()
        self.scores_norm = list()
        self.work_norm = 100
        # Рабочий лимит определяет момент, когда работнику больше не дают новых задач
        # Минимальный лимит - это доля каждого работника по минимальным стоимостям работ для каждого
        # Максимальный лимит - это доля нормы работы на каждого работника
        self.work_limit = 0

        # Данные для хода решения
        # Сумма взятых задач
        self.task_scores_sum = 0
        # Может взять задачу (не перегружен)
        self.free = True
        # Должен взять задачу (недогружен)
        self.need_work = True

        # Данные - результат решения
        self.tasks = list()


class Task:
    def __init__(self):
        # Исходные данные
        self.index = -1
        # Средняя оценка задачи человеком - для рандомайза
        self.middle_score = 0

        # Данные для хода решения
        # Не распределена и может быть взята
        self.free = True
        # Должна быть взята (имеет большую удельную оценку)
        self.need_take = True
        # Минимальная оценка у рабочих
        self.min_score = 1

        # Данные - результат решения
        self.worker = None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main = Main()
    rate = 0.4
    while True:
        txt = input("Введите команду (\"новая\" - новые данные, цифра до 1 - новое распределение с заданным коэф: ")
        if str.lower(txt) == "новая" or str.lower(txt) == "нов" or str.lower(txt) == "н":
            main = Main()
        else:
            try:
                rate = float(txt)
                main.distribute_soft(rate)
            except ValueError:
                print("Неверный формат")


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
