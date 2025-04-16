import requests
import pandas as pd
import os
import streamlit as st


class UN_Population:
    def __init__(self):
        self.base_api_url = "https://population.un.org/dataportalapi/api/v1"
        self.df = None
        self.df_cleaned = None
        self.api_key = os.environ.get("UN_POPULATION_API_KEY")

    def _get_api_key(self):
        """Get API key from session state or prompt user for it"""
        if 'un_api_key' in st.session_state and st.session_state.un_api_key:
            return st.session_state.un_api_key

        if self.api_key:
            st.session_state.un_api_key = self.api_key
            return self.api_key

        return None

    def _check_api_key_input(self):
        api_key = self._get_api_key()
        if not api_key:
            st.warning(
                "UN Population API requires an API key for authentication.")
            st.info(
                "You need to register for an API key at: https://population.un.org/dataportal/user/signup")
            key_input = st.text_input(
                "Enter your UN Population API key:", type="password", key="api_key_input")
            if key_input:
                st.session_state.un_api_key = key_input
                return key_input
            else:
                return None
        return api_key

    def get_indicators(self):
        api_key = self._check_api_key_input()
        if not api_key:
            return {"data": []}

        url = f"{self.base_api_url}/indicators"
        print(f"[API CALL] Requesting indicators from: {url}")

        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error(
                "Unauthorized: Invalid API key. Please check your API key and try again.")
            st.session_state.un_api_key = None
            return {"data": []}
        else:
            raise Exception(
                f"Error fetching indicators: {response.status_code}")

    def get_indicator_names(self):
        """Extract a list of indicator names from the API response"""
        indicators_data = self.get_indicators()

        if 'data' in indicators_data:
            indicator_dict = {indicator['name']: indicator['id']
                              for indicator in indicators_data['data']}
            return indicator_dict
        else:
            return {}

    def get_available_targets(self):
        """Get available target IDs for filtering (countries, regions, etc.)"""
        api_key = self._get_api_key()
        if not api_key:
            return {"data": []}

        url = f"{self.base_api_url}/targets"
        print(f"[API CALL] Requesting targets from: {url}")

        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error(
                "Unauthorized: Invalid API key. Please check your API key and try again.")
            st.session_state.un_api_key = None
            return {"data": []}
        else:
            raise Exception(
                f"Error fetching targets: {response.status_code}")

    def get_data_for_indicator(self, indicator_name, locations=None):
        """Fetch data for a specific indicator by name

        Args:
            indicator_name (str): The name of the indicator
            locations (list, optional): List of location IDs to filter. Defaults to None.
        """
        try:
            api_key = self._get_api_key()
            if not api_key:
                return pd.DataFrame()

            indicators_dict = self.get_indicator_names()

            if indicator_name not in indicators_dict:
                raise Exception(f"Indicator name '{indicator_name}' not found")

            indicator_id = indicators_dict[indicator_name]

            url = f"{self.base_api_url}/data/indicators/{indicator_id}/locations/900"

            if locations:
                url = f"{self.base_api_url}/data/indicators/{indicator_id}/locations/{','.join(map(str, locations))}"

            print(
                f"[API CALL] Requesting data for indicator ID {indicator_id}: {url}")

            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()

                if 'data' in data:
                    records = []
                    for item in data['data']:
                        record = {
                            'year': item.get('timeLabel'),
                            'value': item.get('value'),
                            'location': item.get('location', {}).get('name', 'Unknown'),
                            'variant': item.get('variant', {}).get('name', 'Unknown')
                        }
                        records.append(record)

                    df = pd.DataFrame(records)

                    df['year'] = pd.to_numeric(df['year'], errors='ignore')

                    return df
                else:
                    return pd.DataFrame()
            elif response.status_code == 401:
                st.error(
                    "Unauthorized: Invalid API key. Please check your API key and try again.")
                st.session_state.un_api_key = None
                return pd.DataFrame()
            else:
                raise Exception(f"{response.status_code}")
        except Exception as e:
            raise Exception(f"Error fetching data for {indicator_name}: {e}")

    def get_top_populated_countries(self, limit=10):
        """Get the top populated countries for demonstration"""
        try:
            api_key = self._get_api_key()
            if not api_key:
                return [900]

            indicators_dict = self.get_indicator_names()
            population_indicators = [
                name for name in indicators_dict.keys() if "Total Population" in name]

            if not population_indicators:
                return [900]  # World

            indicator_id = indicators_dict[population_indicators[0]]

            url = f"{self.base_api_url}/data/indicators/{indicator_id}/locations/900"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    location_ids = set()
                    for item in data['data']:
                        if 'location' in item and 'id' in item['location']:
                            location_ids.add(item['location']['id'])

                    return list(location_ids)[:limit]
                else:
                    return [900]
            elif response.status_code == 401:
                st.error(
                    "Unauthorized: Invalid API key. Please check your API key and try again.")
                st.session_state.un_api_key = None
                return [900]
            else:
                return [900]
        except:
            return [900]
