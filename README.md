# HouseCanary API Python Client

The HouseCanary API Python Client provides an easy interface to call the HouseCanary Property API.

## Installation

To install:
```
pip install hc-api-python
```

## Basic Usage


```python   
import housecanary
client = housecanary.HouseCanaryClient("my_auth_key", "my_secret")
result = client.get("value_report", "85 Clay St", "02140", "json")

# result is an instance of HouseCanaryResponse
print result.body_json()
```

## Authentication

When you create an instance of a HouseCanaryClient, you need to give it your API key and secret provided to you by HouseCanary. You can pass these values to the HouseCanaryClient constructor:

```python
client = housecanary.HouseCanaryClient("my_auth_key", "my_secret")
```

Alternatively, instead of passing in your key and secret to the constructor, you can store them in the following environment variables:

- HC_API_KEY
- HC_API_SECRET

Creating an instance of HouseCanaryClient with no arguments will read your key and secret from those environment variables:

```python
client = housecanary.HouseCanaryClient()
```

## Usage Details

### get
The `get` method calls the HouseCanary API with a single address and returns a HouseCanaryResponse.

###### Args:
- **api** (required) -- The endpoint to call. Can be one of:
	- `"value_report"` -- for the Value Report API
	- `"score"` -- for the Property Score API
	- `"avm"` -- for the Automated Valuation Model API
- **address** (optional) -- Building number, street name and unit number. Default is None.
	If specified, zipcode must also be specified. 
- **zipcode** (optional) -- Zipcode that matches the address. Default is None.
	If specified, address must also be specified.
- **format** (optional) -- Output format. Can be "json", "pdf" or "all". 
	The default is "all", which is a zip of all available formats.
	**format** is only used when **api** is set to "value_report"
- **report_type** (optional) -- Type of report. Can be "summary" or "full". The default is "full".
	**report_type** is only used when **api** is set to "value_report"

###### Example:
```python
client = housecanary.HouseCanaryClient()
result = client.get("value_report", "85 Clay St", "02140", "json")
```

### get_multi
The `get_multi` method calls the HouseCanary API with multiple addresses in batch.

###### Args:
- **api** (required) -- The endpoint to call. Can be one of:
	- `"value_report"` -- for the Value Report API
	- `"score"` -- for the Property Score API
	- `"avm"` -- for the Automated Valuation Model API
- **address_list** (required) -- A list used for calling the API with multiple addresses. Can be one of:
	- A two dimensional list of address and zipcode strings
		Example: `[["85 Clay St", "02140"], ["47 Perley Ave", "01960"]]`
	- A list of HouseCanaryProperty objects.
- **format** (optional) -- Output format. Can be "json", "pdf" or "all". 
	The default is "all", which is a zip of all available formats.
	**format** is only used when **api** is set to "value_report"
- **report_type** (optional) -- Type of report. Can be "summary" or "full". The default is "full".
	**report_type** is only used when **api** is set to "value_report"

###### Example with list of address and zipcode strings:
```python
client = housecanary.HouseCanaryClient()
result = client.get_multi("value_report", [["85 Clay St", "02140"], ["47 Perley Ave", "01960"]], "json")
```

###### Example with list of HouseCanaryProperty objects:
```python
client = housecanary.HouseCanaryClient()
addr1 = housecanary.HouseCanaryProperty("85 Clay St", "02140")
addr2 = housecanary.HouseCanaryProperty("47 Perley Ave", "01960")
result = client.get_multi("value_report", [addr1, addr2], "json")
```

The benefit of using a list of HouseCanaryProperty objects is that you can give each object a unique identifier that will be returned in the response to map each address to it's data. Example:

```python
client = housecanary.HouseCanaryClient()
addr1 = housecanary.HouseCanaryProperty("85 Clay St", "02140", "prop_1")
addr2 = housecanary.HouseCanaryProperty("47 Perley Ave", "01960", "prop_2")
result = client.get_multi("value_report", [addr1, addr2], "json")
print result.body_json()
# {"prop_1": { ... }, "prop_2": { ... }}
```

### HouseCanaryResponse
Both the `get` and `get_multi` methods return an instance of HouseCanaryResponse.

###### Notable methods:
- **body** - returns the body of the response from the API as a string.
- **body_json** - returns the body of the response from the API as json if it was valid json.
- **has_business_error** - returns a boolean indicating whether there was an error retrieving data for any of the requested addresses.
- **get_business_error_messages** - returns a list of error messages, if any, that occurred when retrieving data for any of the requested addresses.
- **hc_properties** - returns a list of HouseCanaryProperty objects. Each object has a `data` field that contains the data returned for an individual address.

###### Example:
```python
result = client.get_multi("value_report", [addr1, addr2], "json")
for p in result.hc_properties():
	print p.unique_id
	print p.address
	print p.zipcode
	print p.data
```
