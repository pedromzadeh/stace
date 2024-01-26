from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import requests


class _APICaller(ABC):
    @abstractmethod
    def get():
        pass


class ThingSpeakAPICaller(_APICaller):
    @classmethod
    def get(cls, channel_id, **query_params):
        """
        Fetch data from ThingSpeak.

        Parameters
        ----------
        channel_id : int
            Channel ID to read from.

        **query_params : dict, optional
            Specify any custom query, by default will get the last 10 records.
            See https://www.mathworks.com/help/thingspeak/readdata.html.

        Returns
        -------
        df : pd.DataFrame
            Table containing the fetched data. Columns are "Timestamp",
            "entry_id", and any other fields available when the data was fetched.

        Note
        ----
        If the channel is private, specify API key as `api_key`.
        """
        MAX_BATCH_SIZE = 8000
        query_params = {"results": 10} | query_params

        if query_params["results"] < MAX_BATCH_SIZE:
            return cls.get_single_batch(channel_id, **query_params)
        else:
            return cls.get_multiple_batches(MAX_BATCH_SIZE, channel_id, **query_params)

    @classmethod
    def get_single_batch(cls, channel_id, **query_params):
        custom_query = ""
        for key, val in query_params.items():
            custom_query += str(key) + "=" + str(val) + "&"
        get_url = (
            f"https://api.thingspeak.com/"
            f"channels/{channel_id}/feeds.json?{custom_query[:-1]}"
        )
        query = requests.get(get_url).json()

        # ensure query isn't empty
        if len(query["feeds"]) == 0:
            raise ValueError("No data was fetched.")

        # get descriptive field names
        field_names = cls._get_field_names(query)

        # rename column names
        results_df = pd.DataFrame(query["feeds"]).rename(columns=field_names)

        # convert data type from str to float for all fields
        df = results_df[list(field_names.values())].astype(float)

        # insert at the beginning a column of timestamps
        df.insert(0, "Timestamp", results_df["created_at"].apply(pd.Timestamp))

        return df.sort_values("Timestamp").reset_index(drop=True)

    @classmethod
    def get_multiple_batches(cls, N_MAX, channel_id, **query_params):
        N = query_params.get("results")
        batches = [N_MAX] * (N // N_MAX)
        batches.append(N % N_MAX) if N % N_MAX != 0 else None
        res = []
        start_date = None
        for batch_size in batches:
            _config = (
                query_params | {"results": batch_size, "end": start_date}
                if start_date
                else query_params
            )
            _df = cls.get_single_batch(channel_id, **_config)
            res.append(_df)
            start_date = (
                _df.iloc[0].Timestamp.strftime("%Y-%m-%d %H:%M:%S").replace(" ", "%20")
            )
        return pd.concat(res).sort_values("Timestamp").reset_index(drop=True)

    @staticmethod
    def _get_field_names(query):
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


class USGSAPICaller(_APICaller):
    @classmethod
    def get(cls, query_params, return_api_response=False):
        """
        Get data from usgs.gov.

        Parameters
        ----------
        query_params : dict
            Specifies the GET request.

        return_api_response : bool, optional
            If True, will return the raw JSON response. By default False.

        Returns
        -------
        pd.DataFrame, JSON (optional)
        """
        if query_params["format"] != "json":
            raise NotImplementedError("Can only process JSON formats currently.")

        response = requests.get(
            "https://waterservices.usgs.gov/nwis/iv/", params=query_params
        ).json()

        # list of dicts, length is number of fields
        time_series = response["value"]["timeSeries"]
        n_fields = len(time_series)

        # combine all fields into one dataframe
        table = []
        for k in range(n_fields):
            # get the field name + units
            #   - variableName has units, but in unicode
            #   - take only name from variableName (split)
            #   - take units from unitCode and add to field name
            field_name = time_series[k]["variable"]["variableName"].split(",")[0]
            field_units = time_series[k]["variable"]["unit"]["unitCode"]
            field_name += f" ({field_units})"

            # get to the data
            df = pd.DataFrame.from_dict(time_series[k]["values"][0]["value"])
            df = (
                df.drop(columns=["qualifiers"])
                .astype({"value": np.float16})
                .rename(columns={"value": field_name, "dateTime": "Timestamp"})
            )
            df["Timestamp"] = [pd.Timestamp(t) for t in df["Timestamp"]]
            table.append(df)
        table = pd.concat(table, axis=1)
        table = table.loc[:, ~table.columns.duplicated()].set_index("Timestamp")

        if return_api_response:
            return table, response
        return table
