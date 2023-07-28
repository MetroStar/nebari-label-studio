from nebari.schema import Base
from typing import Optional

from nebari_helm_stage import InputSchema as HelmStageInputSchema

class InputSchema(Base):
    label_studio_chart: HelmStageInputSchema = HelmStageInputSchema()
    