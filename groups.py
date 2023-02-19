import requests
import json
import xml.etree.ElementTree as ElementTree
import xml.dom.minidom as minidom
import xml.parsers.expat as expat
import itertools
from bs4 import BeautifulSoup

session = requests.session()

class GroupInfo():
    # Group info
    groupID64: int
    groupID32: int
    groupName: str
    groupURL: str
    headline: str
    summary: str
    tag: str
    # Avatar
    avatarIcon: str
    avatarMedium: str
    avatarFull: str
    # Member info
    memberCount: int
    membersInChat: int
    membersInGame: int
    membersOnline: int


def get_tag_from_group_page(groupID64) -> str:
    res = session.get(f"https://steamcommunity.com/gid/{groupID64}")

    soup = BeautifulSoup(res.content, "html.parser")
    try:
        tag = soup.find("span", {"class": "grouppage_header_abbrev"}).text
    except:
        tag = ""

    return tag


def get_gid_from_url(name: str) -> str:
    res = session.get(
        f"https://steamcommunity.com/groups/{name}/memberslistxml/?xml=1")

    try:
        xml = ElementTree.fromstring(res.text)
    except:
        pass

    id64 = int(xml.find('groupID64').text)
    id32 = id64 & 0xFFFFFFFF

    return {"groupID64": id64, "groupID32": id32}


def get_group_info(groupID) -> GroupInfo:
    group_info = GroupInfo()
    res = session.get(
        f"https://steamcommunity.com/gid/{groupID}/memberslistxml/?xml=1")

    try:
        minidom.parseString(res.text)
    except expat.ExpatError:
        return

    xml = ElementTree.fromstring(res.text)

    group_info.groupID64 = int(xml.find('groupID64').text)
    group_info.groupID32 = group_info.groupID64 & 0xFFFFFFFF

    for groupName in xml.iter("groupName"):
        group_info.groupName = groupName.text

    for groupURL in xml.iter("groupURL"):
        group_info.groupURL = groupURL.text

    for headline in xml.iter("headline"):
        group_info.headline = headline.text

    for summary in xml.iter("summary"):
        group_info.summary = summary.text

    group_info.tag = get_tag_from_group_page(groupID)

    for avatarIcon in xml.iter("avatarIcon"):
        group_info.avatarIcon = avatarIcon.text

    for avatarMedium in xml.iter("avatarMedium"):
        group_info.avatarMedium = avatarMedium.text

    for avatarFull in xml.iter("avatarFull"):
        group_info.avatarFull = avatarFull.text

    group_info.memberCount = int(xml.find('memberCount').text)

    for membersInChat in xml.iter("membersInChat"):
        group_info.membersInChat = int(membersInChat.text)

    for membersInGame in xml.iter("membersInGame"):
        group_info.membersInGame = int(membersInGame.text)

    for membersOnline in xml.iter("membersOnline"):
        group_info.membersOnline = int(membersOnline.text)

    return group_info

def main():
    # Load JSON
    with open("groups.json", encoding="utf-8") as file:
        groups = json.load(file)

    for i in itertools.count(start = groups[-1]['groupID32'] + 1):
        group_info = get_group_info(i)
        if not group_info:
            continue

        groups.append(group_info)
        print(f"[{group_info.groupID64}] https://steamcommunity.com/groups/{group_info.groupURL}")

        with open("groups.json", "w", encoding="utf-8") as file:
            json.dump(groups, file, default=vars, indent=4)

if __name__ == "__main__":
    main()