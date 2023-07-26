from xml.dom.minidom import parseString

from typing import List

class Manifest:
    """
    AndroidManifest.xml utils used across the project
    """
    @staticmethod
    def get_activities(manifest : str) -> List[str]:
        """
        Get a list of activities declared in the target manifest.

        :param manifest: Path to the decoded AndroidManifest.xml.
        :type manifest: str
        :return: A sorted list of activities.
        :rtype: List[str]
        """
        data = ""
        with open(manifest, 'r') as m:
            data = m.read()
        dom = parseString(data)
        nodes = dom.getElementsByTagName('activity')
        activities = [node.getAttribute("android:name") for node in nodes]
        return sorted(activities)
    @staticmethod
    def get_main_activity(manifest : str) -> str:
        """
        Get the main activity declared in the target manifest.

        :param manifest: Path to the decoded AndroidManifest.xml.
        :type manifest: str
        :return: The name of the main activity
        :rtype: str
        """
        main_activity = None
        data = ""
        with open(manifest, 'r') as m:
            data = m.read()
        dom = parseString(data)
        nodes = dom.getElementsByTagName('activity')
        for node in nodes:
            intent_filters = node.getElementsByTagName('intent-filter')
            if intent_filters:
                for intent_filder in intent_filters:
                    actions = intent_filder.getElementsByTagName('action')
                    categories = intent_filder.getElementsByTagName('category')
                    for action in actions:
                        if action.getAttribute('android:name') == 'android.intent.action.MAIN':
                            for category in categories:
                                if category.getAttribute('android:name') == 'android.intent.category.LAUNCHER':
                                    main_activity = node.getAttribute("android:name")
        return main_activity

    @staticmethod
    def get_permissions(manifest : str) -> List[str]:
        """
        Get a list of permissions declared in the target manifest.

        :param manifest: Path to the decoded AndroidManifest.xml.
        :type manifest: str
        :return: A sorted list of permissions.
        :rtype: List[str]
        """
        data = ""
        with open(manifest, 'r') as m:
            data = m.read()
        dom = parseString(data)
        nodes = dom.getElementsByTagName('uses-permission')
        nodes.extend(dom.getElementsByTagName('uses-permission-sdk-23'))
        permissions = [node.getAttribute("android:name") for node in nodes]
        return sorted(permissions)
    @staticmethod
    def get_libraries(manifest : str) -> List[str]:
       """
        Get a list of activities declared in the target manifest.

        :param manifest: Path to the decoded AndroidManifest.xml.
        :type manifest: str
        :return: A sorted list of activities.
        :rtype: List[str]
        """
       data = ""
       with open(manifest, 'r') as m:
        data = m.read()
        dom = parseString(data)
        nodes = dom.getElementsByTagName('uses-library')
        libraries = [node.getAttribute("android:name") for node in nodes]
        return sorted(libraries)