from klap4.db_entities import SQLBase

# class JSONable:
#     def __json__(self):
#         raise NotImplementedError(f"Class {type(self).__name__} does not implement the .json() interface.")
#
#     def json(self):
#         return self.__json__()


def get_json(sql_object: SQLBase) -> dict:
    dict_data = vars(sql_object).copy()
    dict_data.pop("_sa_instance_state")
    dict_data["id"] = sql_object.id
    return dict_data


def format_object_list(sql_object_list: SQLBase) -> list:
    formatted_list = []
    for item in sql_object_list:
        obj = get_json(item)
        formatted_list.append(obj)
    
    return formatted_list