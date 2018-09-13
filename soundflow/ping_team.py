import soundflow.teams as team_list
import soundflow.se_api as stack_api
from soundflow.utils import Struct
from soundflow.utils import TeamNotFoundError, NoMembersOnlineError


def ping_team(team_name, message, utils):
    members = None
    try:
        members = _find_team(team_name, utils)
    except TeamNotFoundError:
        utils.post_message(f"Unkown team name **{team_name}**")
    except NoMembersOnlineError:
        utils.post_message(f"Currently, no member of the **{team_name}** team is in this room. Use `@Team/{team_name} --members` to get a list of members for this team and ping one of them manually.")

    if members is not None:
        message = f"{_get_pings(members, utils)} {message}"
        utils.post_message(message)

def get_members(team_name, utils):
    se_api = stack_api.se_api(utils.config["stackExchangeApiKey"])

    for team_raw in team_list.teams:
        team = Struct(**team_raw)
        for alias in team.aliases:
            if alias == team_name:
                member_list = ""
                for member in team.members:
                    if member_list == "":
                        member_list = f"The team **{team_name}** has the following members: {se_api.get_user_pingable_name(member, True)}"
                        continue
                    member_list = f"{member_list}, {se_api.get_user_pingable_name(member, True)}"
                utils.post_message(member_list)



def get_online_members(team_name, utils):
    se_api = stack_api.se_api(utils.config["stackExchangeApiKey"])
    members = []

    try:
        members = _find_team(team_name, utils)
    except TeamNotFoundError:
        utils.post_message(f"Unkown team name **{team_name}**")
    except NoMembersOnlineError:
        utils.post_message(f"Currently, no member of the **{team_name}** team is in this room. Use `@Team/{team_name} --members` to get a list of members for this team and ping one of them manually.")

    member_list = ""
    for member in members:
        if member_list == "":
            member_list = f"The following members of the **{team_name}** team are currently in the room: {se_api.get_user_pingable_name(member[0], True)}"
            continue
        member_list = f"{member_list}, {se_api.get_user_pingable_name(member[0], True)}"
    utils.post_message(member_list)

def _find_team(team_name, utils):
    selected_team = None

    #Search the team list for the given alias and return the team if found
    for team_raw in team_list.teams:
        team = Struct(**team_raw)
        for alias in team.aliases:
            if alias == team_name:
                selected_team = team

    if selected_team is None:
        raise TeamNotFoundError

    #Check which users are currently in the room and sort them by their last seen timestamp
    members_online = []

    for u in utils.room.get_pingable_users():
        if u.id in selected_team.members:
            members_online.append((u.id, u.last_seen))

    members_online.sort(key=lambda tup: tup[1])

    if len(members_online) == 0:
        raise NoMembersOnlineError
    else:
        return members_online



def _get_pings(members, utils):
    se_api = stack_api.se_api(utils.config["stackExchangeApiKey"])
    ping_list = ""
    ping_handle = "@" if not utils.debug_mode else "%" # Use "%" as ping handle when debugging and "@" for production

    for member in members:
        username = se_api.get_user_pingable_name(member[0])
        if ping_list == "":
            ping_list = f"{ping_handle}{username}"
            continue
        ping_list = f"{ping_list}, {ping_handle}{username}"

    return ping_list

