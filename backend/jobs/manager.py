from jobs.payment import paymentJob
from jobs.update import updateJob
from jobs.deliver import deliverJob
from redis import Redis
from rq import Queue

redis_con = Redis(host="localhost",port=6379)
task_queue = Queue("task_queue",connection=redis_con)

def rollback_payment_job():
    print("Rolling back changes for paymentJob...")

def rollback_update_job():
    print("Rolling back changes for updateJob...")

def rollback_deliver_job():
    print("Rolling back changes for deliverJob...")

def manager(id):
    print("\n== ", id, " Manager started ==")

    payment_job = task_queue.enqueue(paymentJob,id)
    payment_job.description = "paymentJob"

    update_job = task_queue.enqueue(updateJob, id)
    update_job.description = "updateJob"

    deliver_job = task_queue.enqueue(deliverJob, id)
    deliver_job.description = "deliverJob"