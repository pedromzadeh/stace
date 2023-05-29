import pandas as pd
import requests


class ThingSpeak:

    def __init__(self, channel_id, api_key=None, GET_config=None):
        """
        Initialize a ThingSpeak object for sending HTTPS GET requests.

        Parameters
        ----------
        channel_id : int
            Specifies the channel ID to read from.

        api_key : str, optional
            Must provide if channel is private. By default None, which assumes
            channel is public.

        GET_config : dict
            Specify any custom query, e.g., {"results" : 10} will get the 10 last
            points from the server.
            See https://www.mathworks.com/help/thingspeak/readdata.html for possible
            selections.
        """
        self.channel_id = channel_id
        self.api_key = api_key

        custom_query = ""
        for key, val in GET_config.items():
            custom_query += str(key) + "=" + str(val) + "&"
        custom_query = custom_query[:-1]
        self.get_url = (f"https://api.thingspeak.com/"
                        f"channels/{channel_id}/feeds.json?{custom_query}"
                        )

    def fetch(self):
        """
        Fetches data from a ThingSpeak channel via a GET request.

        Returns
        -------
        df : pd.DataFrame
            Table containing the fetched data. Columns are "timestamp",
            "entry_id", and any other fields available when the data was fetched.
        """
        query = requests.get(self.get_url).json()

        # get descriptive field names
        field_names = self._get_field_names(query)

        # rename column names
        results_df = pd.DataFrame(query["feeds"]).rename(columns=field_names)

        # convert data type from str to float for all fields
        df = results_df[list(field_names.values())].astype(float)

        # insert at the beginning a column of timestamps
        df.insert(0, "timestamp", results_df["created_at"].apply(pd.Timestamp))

        return df

    def _get_field_names(self, query):
        """
        Gets the descriptive field names.

        Parameters
        ----------
        query : dict
            The raw dict fetched from the server.

        Returns
        -------
        field_names : dict
            Keys are "field{i}" generic. Values are the descriptive text.
        """
        desc = query["channel"]
        field_names = {}

        # iterate through the dict, which has keys and values
        for key, val in desc.items():

            # if the key contains "field", then it's a field so store it
            if "field" in str(key):
                field_names[key] = val

        return field_names
