import datetime
import enum
import typing

import dateutil.parser
import justpy as jp



class ItemList(jp.Div):

    def __init__(
            self,
            item_class: type,
            title: str = None,
            bg: str = None,
            **kwargs
    ):
        if "classes" not in kwargs:
            kwargs["classes"] = "m-2 mx-auto flex flex-col outline outline-blue-500  rounded"
        if bg is None:
            bg = "bg-gray-100"
        kwargs["classes"] += f" {bg}"
        super(ItemList, self).__init__(
                **kwargs
        )
        self.item_class = item_class
        if title is not None:
            self.list_title = jp.P(a=self, text=title, classes="mx-4")
        self.item_container = jp.Div(a=self, classes="mx-2")
        self.item_wrappers: typing.List[ItemWrapper] = []
        self.controls_div = jp.Div(a=self)
        self.add_btn = self._setup_add_button()
        self.selection_option_sources = {}

    def _setup_add_button(self,) -> jp.Button:
        return jp.Button(
                a=self.controls_div,
                text="add",
                classes="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mx-4 my-2",
                on_click=self.handle_add_item
        )

    def handle_add_item(self, msg):
        self.add_item()

    def add_item(self, item: jp.HTMLBaseComponent = None):
        if item is None:
            item = self.item_class()
            if self.selection_option_sources is not None:
                item.selection_option_sources = self.selection_option_sources
        item_wrapper = ItemWrapper(a=self.item_container, item=item, manager=self)
        self.item_wrappers.append(item_wrapper)
        self.update_item_titles()
        print(self.get_records())
        if self.selection_option_sources is not None:
            for item in self.get_items():
                fn = getattr(item, "update_selection_options", None)
                if callable(fn):
                    fn()

    def delete_wrapper(self, wrapper: 'ItemWrapper'):
        self.item_wrappers.remove(wrapper)
        self.item_container.remove(wrapper)
        self.update_item_titles()

    def delete_item(self, item):
        for wrapper in self.item_wrappers:
            if wrapper.item == item:
                self.delete_wrapper(wrapper)
                break

    def get_items(self):
        return [wrapper.item for wrapper in self.item_wrappers]

    def get_records(self) -> typing.List[dict]:
        return [item.get_record() for item in self.get_items()]

    def update_item_titles(self):
        for i, item_wrapper in enumerate(self.item_wrappers):
            title = f"{getattr(self.item_class, 'LABEL', '')}#{i+1}"
            item_wrapper.set_title(title)


class ItemWrapper(jp.Div):

    def __init__(
            self,
            item: jp.HTMLBaseComponent,
            manager: ItemList,
            **kwargs
    ):
        super(ItemWrapper, self).__init__(**kwargs, classes="grid grid-cols-2 m-4 p-4 outline outline-1 shadow-xl")
        self.item = item
        self.manager = manager
        self.title_div = jp.Div(a=self, classes="justify-self-start m-2")
        self.del_btn = jp.Button(
                a=self,
                text="❌",
                classes=jp.Styles.button_simple + "flex-none justify-self-end",
                on_click=self.delete_item
        )
        self.wrapper_div = jp.Div(a=self, classes="col-span-2")
        self.wrapper_div.add_component(item)

    def delete_item(self, msg):
        self.manager.delete_wrapper(self)
        self.delete()

    def set_title(self, title: str):
        self.title_div.text = title


class IdSelector(ItemList):
    """
    Selector field for an identifier
    """
    def __init__(self, title:str = None, **kwargs):
        super(IdSelector, self).__init__(item_class=LabeledField, title=title, **kwargs)

    def _setup_add_button(self) -> jp.Button:
        button = jp.Button(
                a=self,
                text="add",
                classes=jp.Styles.button_simple,
                on_click=self.handle_add_item
        )
        self.dropdown = jp.Div(
                a=self,
                classes="z-10 text-base list-none bg-white divide-y divide-gray-100 rounded shadow w-44 dark:bg-gray-700"
        )
        self.dropdown.hidden()
        div2 = jp.Div(a=self.dropdown, classes="py-1")
        SelectionOption(key="wikidata", label="wikidata", selection_callback=self.handle_dropdown_click, a=div2)
        SelectionOption(key="orcid", label="orcid", selection_callback=self.handle_dropdown_click, a=div2)
        return button

    def handle_add_item(self, msg):
        self.dropdown.hidden_toggle()

    def handle_dropdown_click(self, msg):
        self.dropdown.hidden()
        selected_option = msg.target
        new_item = LabeledField(label=selected_option.label, classes="mx-auto")
        setattr(new_item, "key", selected_option.key)
        self.add_item(new_item)

    def get_records(self) -> dict:
        res = {}
        for item in self.get_items():
            key = getattr(item, "key")
            value = item.get_value()
            if key in res:
                res[key] = [res[key], value]
            else:
                res[key] = value
        return res


class SelectionOption(jp.Div):
    """
    option to select
    """

    def __init__(self, key: str, label: str, selection_callback: typing.Callable, **kwargs):
        """
        constructor
        """
        super(SelectionOption, self).__init__(
                on_click=selection_callback,
                **kwargs)
        self.key = key
        self.label = label
        self.selection_callback = selection_callback
        self.div = jp.Li(
                a=self,
                classes="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white"
        )
        jp.P(a=self.div, text=self.label)


class InputTypes(enum.Enum):
    """
    html input field input types
    """
    TEXT = "text"
    TEXT_AREA = "textarea"
    DATE = "date"
    SELECT = "select"


class LabeledField(jp.Div):
    """
    Field with attached label
    """

    def __init__(self, label: str, value=None, input_type: InputTypes = InputTypes.TEXT, **kwargs):
        """
        constructor
        Args:
            label: label of the field
            value: initial value of the field
            kwargs: further arguments
        """
        if "classes" not in kwargs:
            kwargs["classes"] = "m-4"
        super(LabeledField, self).__init__(**kwargs)
        self.input_type = input_type
        self.label = jp.Label(
                a=self,
                classes="block text-sm font-medium text-gray-700",
                text=label
        )
        field_classes = "w-full mt-1 block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        if input_type is InputTypes.TEXT_AREA:
            self.field = jp.Textarea(
                    a=self,
                    type=input_type.value,
                    value=value,
                    classes=field_classes
            )
        elif input_type is InputTypes.SELECT:
            self.field = jp.Select(a=self, value=value, classes=field_classes)
        else:
            self.field = jp.Input(
                    a=self,
                    type=input_type.value,
                    value=value,
                    classes=field_classes
            )

    def get_value(self):
        value = self.field.value
        if self.input_type is InputTypes.DATE and value is not None:
            value = dateutil.parser.parse(value).date()
        return value

    def set_value(self, value):
        self.field.value = value


