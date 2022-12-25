from io import BytesIO
from xml.etree import ElementTree


def dict_to_element(data, root: ElementTree.Element = None, root_name: str = "root") -> ElementTree:
    """
    Convert data to ElementTree.Element
    :param data: input data
    :param root: xml root element
    :param root_name: name of root element
    :return: (ElementTree)

    """
    if root is None:
        root = ElementTree.Element(root_name)
    if isinstance(data, list):
        for item in data:
            element = ElementTree.SubElement(root, "item")
            if isinstance(item, list) or isinstance(item, dict):
                dict_to_element(item, element)
            else:
                element.text = str(item)

    elif isinstance(data, dict):
        for key, value in data.items():
            element = ElementTree.SubElement(root, str(key))
            if isinstance(value, list) or isinstance(value, dict):
                dict_to_element(value, element)
            else:
                element.text = str(value)

    return ElementTree.ElementTree(root)


def toXML(tree: ElementTree) -> bytes:
    """
    Convert ElementTree into xml
    :param tree: input tree
    :return: xml

    """
    ElementTree.indent(tree, space="\t", level=0)
    # using write instead tostring to add XML declaration
    output = BytesIO()
    tree.write(output, encoding="utf-8", xml_declaration=True)
    return output.getvalue()


def dict_to_xml(data, root_name: str = "root") -> bytes:
    """
    Convert data to xml string
    :param data: input data
    :param root_name: name of root element
    :return: xml string

    """
    tree = dict_to_element(data, root_name=root_name)
    return toXML(tree)
