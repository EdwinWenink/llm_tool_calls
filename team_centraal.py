import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load .env as environment variables in runtime
load_dotenv()
USERNAME = 'ChatNS'
PASSWORD = os.getenv('TEAM_CENTRAAL_PASSWORD')
BASE_URL = 'https://teamcentraal-a.ns.nl/odata/POS_Odata_v4'
USER_AGENT = 'ChatNSTEST'


class Rol(BaseModel):
    ID: int
    Rolnaam: str
    Leadrol: bool | None
    Lead: bool | None
    Ondertitel: str | None
    ClusterRol: bool | None
    ResultaatgebiedRol: bool | None

class DepartmentFinalBase(BaseModel):
    ID: int
    DepartmentId: int | None
    Parent: str | None
    Active: bool | None
    Name: str
    Description: str | None
    DepartmentFullName: str | None
    SYSID: str | None
    IsBOIT: bool | None
    Url: str | None

class ResultaatGebiedBase(BaseModel):
    ID: int
    Soort: str | None
    Naam: str | None
    Code: str | None

class TeamCentraalBetrokkene(BaseModel):
    ID: int
    Naam: str | None
    Email: str | None
    UPN: str | None
    Rol: Rol
    # Expand options
    DepartmentFinal: DepartmentFinalBase | None = None
    ResultaatGebied: ResultaatGebiedBase| None = None

class AccountBase(BaseModel):
    ID: int
    FullName: str
    Email: str

class FunctieRolsBase(BaseModel):
    ID: int
    RolNaam: str
    ScrumMasterProductOwner: str | None
    Active: bool


class TeamMemberBase(BaseModel):
    """
    Note that TeamMemberBase and TeamCentraalTeam are circularly dependent.
    By placing 'TeamCentraalTeam' in quotes, we can do a forward annotation.
    """
    ID: int
    Admin: bool
    Actief: bool
    # Expand options
    Account: AccountBase | None = None
    Coach_Team: 'TeamCentraalTeam' | None = None
    FunctieRols: FunctieRolsBase | None = None
    TeamMember_Team: 'TeamCentraalTeam' | None = None


class TeamCentraalTeam(BaseModel):
    ID: int
    Naam: str
    Ambitie: str | None
    Projecten: str | None
    Vaardigheden: str | None
    OmschrijvingTeam: str | None
    OmschrijvingTeamServiceNow: str | None
    TeamCategory: str
    WorkingOnApplications: str | None
    # Expand options
    Team_Department: DepartmentFinalBase | None = None
    Team_Members: list[TeamMemberBase] | None = None


class TeamCentraalBetrokkeneResponse(BaseModel):
    """/Betrokkenens"""
    odata_context: str = Field(alias='@odata.context')
    value: list[TeamCentraalBetrokkene]


class TeamCentraalTeamResponse(BaseModel):
    '''/Teams'''
    odata_context: str = Field(alias='@odata.context')
    value: list[TeamCentraalTeam]


class TeamCentraalTeamMemberResponse(BaseModel):
    '''/Teams'''
    odata_context: str = Field(alias='@odata.context')
    value: list[TeamMemberBase]


def who_is(name: str) -> str:
    """
    Function that returns the information of a person from the Team Centraal database.
    This queries the "betrokkenens" endpoint, which is synced with Azure AD. However,
    not every "betrokkene" is part of a team and as such, I didn't find a direct link
    to relate "betrokkene" and "team". For a "betrokkene" only RG and department are linked.
    This is why we enrich the response with the `find_team_of_person` function, which
    queries starting from /TeamMembers.
    """

    endpoint=f"{BASE_URL}/Betrokkenens?$expand=ResultaatGebied,DepartmentFinal,Rol&$filter=contains(Naam, '{name}')"

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': USER_AGENT
    }

    response = requests.get(endpoint, auth=(USERNAME, PASSWORD), headers=headers, timeout=60)
    print(response)
    print(response.status_code)
    print(response.json())

    if response.status_code == 200:
        validated_response = TeamCentraalBetrokkeneResponse.model_validate(response.json())
        persons = validated_response.value
        answer = "\n".join([ f"{person.Naam} is {person.Rol.Rolnaam} bij {person.DepartmentFinal.Name if person.DepartmentFinal else '[onbekende afdeling]'}" for person in persons])
        return answer
    else:
        return 'Persons is not found.'


def find_team_of_person(name: str) -> str:
    '''
    Queries "TeamMembers" on a person to retrieve the Team information for that person.
    Differs from "Betrokkenens" because these are not necessarily part of a team.
    '''
    endpoint = f"{BASE_URL}/TeamMembers?$expand=Account&$filter=contains(Account/FullName, '{name}')&$expand=Account,TeamMember_Team"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': USER_AGENT
    }

    response = requests.get(endpoint, auth=(USERNAME, PASSWORD), headers=headers, timeout=60)
    print(response)
    print(response.status_code)
    print(response.json())

    if response.status_code == 200:

        validated_response = TeamCentraalTeamMemberResponse.model_validate(response.json())
        teams = validated_response.value
        # TODO handle situation where multiple persons are found.

        # TODO handle situation where duplicates are found.
        # Merge teams (make auxiliary function).

        # TODO adjust answer
        '''
        answer = "\n".join([
             f"{team.Naam} is een {team.TeamCategory} team dat werkt aan {team.WorkingOnApplications if team.WorkingOnApplications else ''} {team.Projecten if team.Projecten else ''}."
               f"Beschrijving: {team.OmschrijvingTeamServiceNow if team.OmschrijvingTeamServiceNow else ''}{team.OmschrijvingTeam if team.OmschrijvingTeam else ''}"
               f"Skills: {team.Vaardigheden if team.Vaardigheden else ''}"  for team in teams]
               )
        '''
        answer = ''
        return answer

    else:
        return 'Team is not found'



def get_team_info(team_name: str) -> str:
    """
    Function that returns the information of a team from the Team Centraal database.
    """
    endpoint = f"{BASE_URL}/Teams?$filter=Naam eq '{team_name}'&$expand=TeamMembers($expand=Account,FunctieRols),Team_Department"

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': USER_AGENT
    }

    response = requests.get(endpoint, auth=(USERNAME, PASSWORD), headers=headers, timeout=60)
    print(response)
    print(response.status_code)
    print(response.json())

    if response.status_code == 200:

        validated_response = TeamCentraalTeamResponse.model_validate(response.json())
        teams = validated_response.value
        # TODO add department
        # TODO add members
        answer = "\n".join([
             f"{team.Naam} is een {team.TeamCategory} team dat werkt aan {team.WorkingOnApplications if team.WorkingOnApplications else ''} {team.Projecten if team.Projecten else ''}."
               f"Beschrijving: {team.OmschrijvingTeamServiceNow if team.OmschrijvingTeamServiceNow else ''}{team.OmschrijvingTeam if team.OmschrijvingTeam else ''}"
               f"Skills: {team.Vaardigheden if team.Vaardigheden else ''}"  for team in teams]
               )
        return answer
    else:
        return 'Team is not found'


if __name__ == "__main__":
    print(who_is("Strikwerda"))
    print(get_team_info("Knipteam"))
    print(find_team_of_person('Strikwerda'))