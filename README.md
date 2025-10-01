# Weather Monitoring System

A command-line interface tool that processes and displays real-time meteorological data fetched from the [Hong Kong Observatory (HKO) Open Data API](https://www.hko.gov.hk/en/abouthko/opendata_intro.htm). It aims to keep users alerts and informed about latest weather conditions in Hong Kong, especially during extreme weather events such as rainstorms and typhoons.

## Table of Contents

- [Description](#description)
  - [Types of Meteorological Data](#types-of-meteorological-data)
  - [Extreme Weather Events](#extreme-weather-events)
    - [Tropical Cyclones](#tropical-cyclones)
- [Getting Started](#getting-started)
  - [Dependencies](#dependencies)
  - [Usage](#usage)

## Description

### Types of Meteorological Data

The system captures a wide range of real-time meteorological data, including

- [Rainfall in the past hour from automatic weather station](https://data.gov.hk/en-data/dataset/hk-hko-rss-rainfall-in-the-past-hour)
- [Latest 10-minute mean wind direaction, wind speed, and maximum gust](https://data.gov.hk/en-data/dataset/hk-hko-rss-latest-ten-minute-wind-info)
- [Latest tidal information](https://data.gov.hk/en-data/dataset/hk-hko-rss-latest-tidal-info)
- [Latest 1-minute mean sea level pressure](https://data.gov.hk/en-data/dataset/hk-hko-rss-latest-one-minute-mean-sea-level-pressure)

### Extreme Weather Events

During extreme weather events such as rainstorms and typhoons, the system will keep users up to date by regularly updating crucial information from the following sources

- [Latest weather warning information](https://data.gov.hk/en-data/dataset/hk-hko-rss-weather-warning-information)
- [Special weather tips](https://data.gov.hk/en-data/dataset/hk-hko-rss-special-weather-tips)
- [Tropical cyclone track information (past and forecasted)](https://data.gov.hk/en-data/dataset/hk-hko-rss-tc-track-info)
  - Distance to Hong Kong
  - Intensity
  - Maximum Wind Speed

#### Tropical Cyclones

When the Standby Signal No.1 is in force, the system also provides tracking and analytics for key tropical cyclone metrics, including

- Maximum 60-minute mean speed
- Gust peak speed
- Closest distance to Hong Kong
- Minimum 1-minute mean sea level pressure
- Sea level above chart datum

It enables a preliminary quantitative strength analysis with historical cyclones.

## Getting Started

### Dependencies

Use the package manager `pip` to install the dependencies for this project.

`$ pip install -r requirements.txt`

### Usage

#### Tropical Cyclone Track and Forecast Information

`$ python cycloneTrack.py`

It is capable to track more than one tropical cyclones.

Track information in: `data/tropicalCyclones/{tropical_cyclone_name}/{tropical_cyclone_name}_track.xlsx`

Forecast information in: `data/tropicalCyclones/{tropical_cyclone_name}/{tropical_cyclone_name}_forecast.xlsx`

#### Hourly Rainfall

`$ python rainfall.py`

Results in: `data/rainfall/latest_rainfall.csv`

#### 10-minute mean wind direaction, wind speed, and maximum gust

`$ python windinfo.py`

Results in: `data/windinfo/latest_windinfo.csv`

#### Tides information

`$ python seaLevelTracking.py`
