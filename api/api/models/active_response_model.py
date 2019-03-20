# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from api.models.base_model_ import Model
from api import util


class ActiveResponse(Model):

    def __init__(self, command: str=None, custom: bool=False, arguments: List[str]=None):
        """ActiveResponse body model

        :param command: Command running in the agent. If this value starts by !, then it refers to a script name instead of a command name
        :type command: str
        :param custom: Whether the specified command is a custom command or not
        :type custom: bool
        :param arguments: Command arguments
        :type arguments: str
        """
        self.swagger_types = {
            'command': str,
            'custom': bool,
            'arguments': List[str]
        }

        self.attribute_map = {
            'command': 'command',
            'custom': 'custom',
            'arguments': 'arguments'
        }

        self._command = command
        self._custom = custom
        self._arguments = arguments

    @classmethod
    def from_dict(cls, dikt) -> Dict:
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Agent of this Agent.
        :rtype: dict
        """
        return util.deserialize_model(dikt, cls)

    @property
    def command(self) -> str:
        """
        :return: Command to run in the agent
        :rtype: str
        """
        return self._command

    @command.setter
    def command(self, command: str):
        """Command running in the agent.

        :param command: Command to run in the agent
        """
        self._command = command

    @property
    def custom(self) -> bool:
        """
        :return: Whether the specified command is a custom command or not
        :rtype: bool
        """
        return self._custom

    @custom.setter
    def custom(self, custom: bool):
        """
        :param command: Whether the specified command is a custom command or not
        """
        self._custom = custom

    @property
    def arguments(self) -> List[str]:
        """
        :return: Command arguments
        :rtype: str
        """
        return self._command

    @arguments.setter
    def arguments(self, arguments: List[str]):
        """Command running in the agent.

        :param arguments: Command arguments
        """
        self._arguments = arguments