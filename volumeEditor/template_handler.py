import typing
from datetime import datetime

from addict import Dict


class VolumePageTemplate():
    """
    Renders volume index page
    """

    def __init__(self):
        """
        constructor
        """
        #self.volume_page_template = f"{self.__file__}/templates/volume_index.jinja"

    def render(self, volume_record: typing.Union[dict, Dict]) -> str:
        if not isinstance(volume_record, Dict):
            volume_record = Dict(volume_record)
        from jinja2 import Environment, PackageLoader, select_autoescape
        env = Environment(loader=PackageLoader("volparser"), autoescape=select_autoescape())
        template = env.get_template("volume_index.jinja2")
        return template.render(
                volume=volume_record,
                datetime=datetime,
                enumerate=enumerate,
                len=len
        )
