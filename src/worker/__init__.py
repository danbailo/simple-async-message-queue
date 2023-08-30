from dataclasses import dataclass

from enum import StrEnum

from common.logger import logger

from .sample_worker import SampleWorker
from .sample_worker_always_success import SampleWorkerAlwaysSuccess


class WorkerEnum(StrEnum):
    sample_worker = 'sample-worker'
    sample_worker_always_success = 'sample-worker-always-success'


@dataclass
class InitWorker:
    worker: WorkerEnum

    MAPPED_WORKER = {
        WorkerEnum.sample_worker: SampleWorker,
        WorkerEnum.sample_worker_always_success: SampleWorkerAlwaysSuccess,
    }

    def __new__(cls, worker: WorkerEnum):
        logger.info('initializing worker...')
        return cls.MAPPED_WORKER[worker]()
