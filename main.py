from random import Random
import sys
import os
# This is a sample Python script.


class Worker:
    def __init__(self):
        # Исходные данные
        self.index = -1
        self.name = ""
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
        self.name = ""
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


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
class Main:
    def __init__(self):
        # Задачи
        self.count_tasks = 16
        self.tasks = list()
        # self.task_middle_score = list()
        r = Random()
        for i in range(self.count_tasks):
            new_task = Task()
            new_task.index = i
            new_task.name = "T_" + str(i)
            new_task.middle_score = int(r.random() * r.random() * r.random() * 200 + 10)
            # print("middle = " + str(new_task.middle_score))
            self.tasks.append(new_task)

        # Работники
        self.count_workers = 4
        self.workers = list()
        # work_norm_sum = 0
        for i in range(self.count_workers):
            new_worker = Worker()
            new_worker.index = i
            new_worker.name = "Worker " + str(i)
            # Всем для начала одинаковое количество работы на выработку
            new_worker.work_norm = 25 + 25 * i
            # if i == 0:
            #     new_worker.work_norm = 40
            # work_norm_sum += new_worker.work_norm
            # sum_scores = 0
            for task in self.tasks:
                score = task.middle_score
                for j in range(3):
                    score *= (1 + r.random())
                    score /= (1 + r.random())

                new_worker.scores.append(int(score))
                # sum_scores += int(score)

            # for score in new_worker.scores:
            #     new_worker.scores_norm.append(round(score / sum_scores, 6))

            self.workers.append(new_worker)

        # Определение лимита работы для каждого
        # for worker in self.workers:
        #     worker.work_limit = worker.work_norm / work_norm_sum
        # # Лимит работы уменьшаем в сторону минимальных оценок
        # min_scores_sum = 0
        # for task in self.tasks:
        #     task.min_score = sys.float_info.max
        #     for worker in self.workers:
        #         if task.min_score > worker.scores_norm[task.index]:
        #             task.min_score = worker.scores_norm[task.index]
        #
        #     min_scores_sum += task.min_score
        # # Берем пределом работ среднее между средним лимитом и лимитом минимальной оценки
        # reduction_rate = min_scores_sum + 0.5 * (1 - min_scores_sum)
        # self.prepare()

    def prepare(self):
        work_norm_sum = 0
        for worker in self.workers:
            work_norm_sum += worker.work_norm
            sum_scores = 0
            for task in self.tasks:
                sum_scores += int(worker.scores[task.index])

            for score in worker.scores:
                worker.scores_norm.append(round(score / sum_scores, 6))

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
        for worker in self.workers:
            # worker.work_limit *= reduction_rate
            print(worker.name + "(lim=" + str(round(worker.work_limit, 3)) + ") score "
                  + str(worker.scores_norm))

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
            worker.scores_norm = list()
        self.prepare()
        if overwork_rate == 0:
            overwork_rate = 0.01
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

        distribute_string = ""
        iii = 0
        while free_tasks_count and free_workers_count:
            iii += 1
            # Ищем самого незагруженого работника
            # lazy_worker_score = sys.float_info.max
            # for worker in self.workers:
            #     if worker.free:
            #         if lazy_worker_score > worker.task_scores_sum:
            #             lazy_worker_score = worker.task_scores_sum

            for task in self.tasks:
                if task.free:
                    task.need_take = True

            # Ищем наибольший перекос
            max_delta = -sys.float_info.max
            max_delta_index = -1
            for i in range(self.count_tasks):
                if self.tasks[i].free and self.tasks[i].need_take:
                    task_workers_list = list()
                    # min_score = sys.float_info.max
                    # min_worker = None
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
                            # if min_score > worker.scores_norm[i]:
                            #     min_score = worker.scores_norm[i]
                            #     min_worker = worker
                    avg_score /= count
                    score_delta = 0.0
                    rate_next = 0.5
                    task_workers_sorted_list = sorted(task_workers_list, key=lambda work: work[1])

                    min_worker = task_workers_sorted_list[0][0]
                    min_score = task_workers_sorted_list[0][1]
                    for worker_score in task_workers_sorted_list[1:]:
                        # score_delta += (worker_score[1] + worker_score[0].task_scores_sum * overwork_rate
                        #                 - min_score - min_worker.task_scores_sum * overwork_rate) * rate_next
                        score_delta += (worker_score[1] - min_score) * rate_next
                        rate_next /= 2
                    # overwork_rate
                    score_delta *= (overwork_rate * min_worker.work_limit
                                    - (min_worker.task_scores_sum + min_score / 2)
                                    ) / (overwork_rate * min_worker.work_limit)

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

            distribute_string += (worker_min_score.name + " <= " + self.tasks[max_delta_index].name + ": "
                                  + str(round(worker_min_score.scores_norm[max_delta_index], 3))
                                  + "(+" + str(round(worker_min_score.scores_norm[max_delta_index]
                                                     - self.tasks[max_delta_index].min_score, 3)) + ")   "
                                  )
            if iii % 5 == 0:
                distribute_string += "\r\n"

            self.tasks[max_delta_index].free = False
            self.tasks[max_delta_index].need_take = False
            self.tasks[max_delta_index].worker = worker_min_score
            worker_min_score.tasks.append(self.tasks[max_delta_index])
            worker_min_score.task_scores_sum += worker_min_score.scores_norm[max_delta_index]
            if worker_min_score.task_scores_sum > worker_min_score.work_limit:
                worker_min_score.free = False
                # print("Worker limit " + str(worker_min_score.index))
            free_tasks_count -= 1

        print(distribute_string)
        print("distributed!")
        all_task_sum = 0
        for worker in self.workers:
            tasks_list = list()
            for task in worker.tasks:
                tasks_list.append(task.name)
            print(worker.name + ": " + str(round(worker.task_scores_sum, 3))
                  + "\t" + str(tasks_list))
            all_task_sum += worker.task_scores_sum
        print("all worker sum = " + str(round(all_task_sum, 3)))

    # Функция, распределяющая задачи по сотрудникам целыми
    # def distribute(self):
    #     # Коэффициент, определяющий насколько загруженность работника должна превышить минимальную среди всех
    #     # чтобы ему не участвовать в следующем конкурсе распределения работ
    #     worker_engagement_rate = 0.15
    #
    #     free_workers_count = self.count_workers
    #     free_tasks_count = self.count_tasks
    #     undistributed = 0
    #     work_norm_sum = 0
    #     # Максимальный лимит работы среди работников
    #     max_work_limit = 0
    #     for worker in self.workers:
    #         if max_work_limit < worker.work_limit:
    #             max_work_limit = worker.work_limit
    #         work_norm_sum += worker.work_norm
    #         for i in range(self.count_tasks):
    #             undistributed += worker.scores_norm[i]
    #
    #     distribute_string = ""
    #     while free_tasks_count and free_workers_count:
    #         # Ищем самого незагруженого работника
    #         lazy_worker_score = sys.float_info.max
    #         for worker in self.workers:
    #             if worker.free:
    #                 if lazy_worker_score > worker.task_scores_sum:
    #                     lazy_worker_score = worker.task_scores_sum
    #
    #         # Помечаем работников, которым положено взять работу
    #         for worker in self.workers:
    #             if worker.free:
    #                 worker.need_work = worker.task_scores_sum \
    #                                    <= lazy_worker_score + worker_engagement_rate * worker.work_limit
    #
    #         # # Коэффициент определяет насколько работа должна быть оценена меньше максимальной
    #         # # чтобы ее рассматривать в работу
    #         # task_engagement_rate = 0.7
    #         # # Коэффициент, определяющий - какой относительно рабочего лимита должна быть оценка задачи
    #         # # чтобы проводить конкурс задач на рассмотрение их в работу
    #         # big_task_rate = 1.0
    #         # # Ищем самую тяжелооцененную работу
    #         # harder_task_score = 0
    #         # for task in self.tasks:
    #         #     if task.free:
    #         #         min_task_score = sys.float_info.max
    #         #         for worker in self.workers:
    #         #             if worker.free:
    #         #                 if min_task_score > worker.scores_norm[task.index]:
    #         #                     min_task_score = worker.scores_norm[task.index]
    #         #         if harder_task_score < min_task_score:
    #         #             harder_task_score = min_task_score
    #
    #         # # Помечаем - какие работы нужно разобрать сейчас
    #         # if harder_task_score >= big_task_rate * max_work_limit:
    #         #     print("hard task!")
    #         #     for task in self.tasks:
    #         #         if task.free:
    #         #             min_task_score = sys.float_info.max
    #         #             for worker in self.workers:
    #         #                 if worker.free:
    #         #                     if min_task_score > worker.scores_norm[task.index]:
    #         #                         min_task_score = worker.scores_norm[task.index]
    #         #             task.need_take = min_task_score >= task_engagement_rate * harder_task_score
    #         # else:
    #         for task in self.tasks:
    #             if task.free:
    #                 task.need_take = True
    #
    #         # Ищем наибольший перекос
    #         max_delta = -1
    #         max_delta_index = -1
    #         for i in range(self.count_tasks):
    #             if self.tasks[i].free and self.tasks[i].need_take:
    #                 task_scores_list = list()
    #                 min_score = sys.float_info.max
    #                 avg_score = 0.0
    #                 # Хорошо было бы оценивать не по average, а как-то сложнее ???
    #                 count = 0
    #                 for worker in self.workers:
    #                     if worker.free:
    #                         task_scores_list.append(worker.scores_norm[i])
    #                         # if max_score < worker.scores_norm[i]:
    #                         #     max_score = worker.scores_norm[i]
    #                         avg_score += worker.scores_norm[i]
    #                         count += 1
    #                         if worker.need_work and min_score > worker.scores_norm[i]:
    #                             min_score = worker.scores_norm[i]
    #                 avg_score /= count
    #                 score_delta = 0.0
    #                 rate = 1.0
    #                 task_scores_list.sort()
    #                 for score in task_scores_list:
    #                     if score >= min_score:
    #                         score_delta += (score - min_score) * rate
    #                         rate /= 2
    #
    #                 # if max_delta < avg_score - min_score:
    #                 if max_delta < score_delta:
    #                     # max_delta = avg_score - min_score
    #                     max_delta = score_delta
    #                     max_delta_index = i
    #
    #         # min_score = sys.float_info.max
    #         # for worker in self.workers:
    #         #     if worker.need_work:
    #         #         if min_score > worker.scores_norm[max_delta_index]:
    #         #             min_score = worker.scores_norm[max_delta_index]
    #         #             worker_min_score = worker
    #         min_score = sys.float_info.max
    #         # if not worker_min_score.free:
    #         #     print("Worker " + str(worker_min_score.index) + " не получил работу " + str(max_delta_index))
    #         for worker in self.workers:
    #             if worker.free and worker.need_work:
    #                 if min_score > worker.scores_norm[max_delta_index]:
    #                     min_score = worker.scores_norm[max_delta_index]
    #                     worker_min_score = worker
    #
    #         # Присвоение задачи
    #         distribute_string += worker_min_score.name + "<=" + str(max_delta_index) + ": "\
    #                              + str(round(worker_min_score.scores_norm[max_delta_index], 3))\
    #                              + "(+" + str(round(worker_min_score.scores_norm[max_delta_index]
    #                                                 - self.tasks[max_delta_index].min_score, 3)) + ")  "
    #
    #         self.tasks[max_delta_index].free = False
    #         self.tasks[max_delta_index].need_take = False
    #         worker_min_score.tasks.append(self.tasks[max_delta_index])
    #         worker_min_score.task_scores_sum += worker_min_score.scores_norm[max_delta_index]
    #         if worker_min_score.task_scores_sum > worker_min_score.work_limit:
    #             worker_min_score.free = False
    #             worker_min_score.need_work = False
    #             # print("Worker limit " + str(worker_min_score.index))
    #         free_tasks_count -= 1
    #
    #     print(distribute_string)
    #     print("distributed!")
    #     for worker in self.workers:
    #         tasks_list = list()
    #         for task in worker.tasks:
    #             tasks_list.append(task.index)
    #         print("Worker " + str(worker.index) + ": " + str(round(worker.task_scores_sum, 3))
    #               + "\t" + str(tasks_list))

    def save_to_file(self):
        file_name = input("Введите имя файла: ")
        if file_name:
            file_name = os.path.join("save", file_name)
            f = open(file_name, "w")
            for worker in self.workers:
                f.write("worker\n")
                f.write(worker.name + "\n")
                f.write(str(worker.index) + "\n")
                f.write(str(worker.scores).replace('[', '').replace(']', '') + "\n")
                # f.write(str(worker.scores_norm).replace('[', '').replace(']', '') + "\n")
                f.write(str(worker.work_norm) + "\n")
                # f.write(str(worker.work_limit) + "\n")

            for task in self.tasks:
                f.write("task\n")
                f.write(task.name + "\n")
                f.write(str(task.index) + "\n")
                f.write(str(task.min_score) + "\n")
            print("saved to " + file_name)

    def load_from_file(self):
        file_name = input("Введите имя файла: ")
        if file_name:
            file_name = os.path.join("save", file_name)
            if os.path.exists(file_name):
                self.workers = list()
                self.tasks = list()
                f = open(file_name, "r")
                st = f.readline().replace("\n", "")
                while st:
                    if st == "worker":
                        new_worker = Worker()
                        new_worker.name = f.readline().replace('\n', '')
                        new_worker.index = int(f.readline().replace('\n', ''))
                        new_worker.scores = [int(i) for i in f.readline().replace('\n', '').split(', ')]
                        # new_worker.scores_norm = [float(i) for i in f.readline().replace('\n', '').split(', ')]
                        new_worker.work_norm = float(f.readline().replace('\n', ''))
                        # new_worker.work_limit = float(f.readline().replace('\n', ''))
                        self.workers.append(new_worker)
                    elif st == "task":
                        new_task = Task()
                        new_task.name = f.readline().replace('\n', '')
                        new_task.index = int(f.readline().replace('\n', ''))
                        # new_task.min_score = float(f.readline().replace('\n', ''))
                        self.tasks.append(new_task)
                    st = f.readline().replace("\n", "")
                self.count_workers = len(self.workers)
                self.count_tasks = len(self.tasks)
                print("loaded from " + file_name)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main = Main()
    rate = 0.4
    while True:
        txt = input("Введите команду (\"новая\",\"сохранить\", \"загрузить\", \"выход\", цифра до 1 - новое решение: ")
        if str.lower(txt) == "новая" or str.lower(txt) == "нов" or str.lower(txt) == "н":
            main = Main()
        elif str.lower(txt) == "выход" or str.lower(txt) == "вых" or str.lower(txt) == "в":
            break
        elif str.lower(txt) == "сохранить" or str.lower(txt) == "сохр" or str.lower(txt) == "с" \
                or str.lower(txt) == "c":
            main.save_to_file()
        elif str.lower(txt) == "загрузить" or str.lower(txt) == "загр" or str.lower(txt) == "з":
            main.load_from_file()
        else:
            try:
                rate = float(txt)
                main.distribute_soft(rate)
            except ValueError:
                print("Неверный формат")


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
