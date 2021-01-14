from .base_model import BaseModel
from .storage_config_data import StorageConfigData
from .network_config_data import NetworkConfigData


class MachineData(BaseModel):
    hostname: str
    storage: StorageConfigData
    network: NetworkConfigData
