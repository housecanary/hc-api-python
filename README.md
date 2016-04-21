# HouseCanary API Python Client

The HouseCanary API Python Client provides an easy interface to call the HouseCanary API.

## Installation

To install:
```
pip install hc-api-python
```

## Basic Usage


```python   
import housecanary
client = housecanary.ApiClient("my_auth_key", "my_secret")
result = client.property.score(("85 Clay St", "02140"))

# result is an instance of HouseCanaryResponse
print result.json()
```

## Authentication

When you create an instance of an ApiClient, you need to give it your API key and secret provided to you by HouseCanary. You can pass these values to the ApiClient constructor:

```python
client = housecanary.ApiClient("my_auth_key", "my_secret")
```

Alternatively, instead of passing in your key and secret to the constructor, you can store them in the following environment variables:

- HC_API_KEY
- HC_API_SECRET

Creating an instance of ApiClient with no arguments will read your key and secret from those environment variables:

```python
client = housecanary.ApiClient()
```

## Usage Details

### Endpoint methods
The ApiClient class provides a `property` wrapper which contains various methods for calling the different endpoints of the HouseCanary API:

- **consumer**
- **flood**
- **school**
- **value**
- **value_forecast**
- **score**
- **zip_hpi_historical**
- **zip_hpi_forecast**
- **rental_value**
- **msa_details**
- **mortgage_lien**
- **ltv**
- **ltv_forecast**
- **owner_occupied**
- **details**
- **sales_history**
- **mls**
- **nod**
- **census**

More wrapper objects may be added to ApiClient later like "zipcode" and "lat_lng".

###### Args:
All of the above endpoint methods take an `address_data` argument. `address_data` can be in one of two forms:

A Json formatted list like:
```python
[{"address":"82 County Line Rd", "zipcode":"72173", "meta":"extra info"}]
```
Or, a list of (address, zipcode, meta) tuples like:
```python
[("82 County Line Rd", "72173", "extra info")]
```
The "meta" field is optional.
If you're only providing one address, you can provide a tuple on it's own:
```python
("82 County Line Rd", "72173")
```

All the endpoint methods of this class return a HouseCanaryResponse object, or the output of a custom OutputGenerator if one was specified in the constructor.

###### Example:
```python
client = housecanary.ApiClient()
result = client.propery.value([("85 Clay St", "02140"), ("82 County Line Rd", "72173")])
```

### HouseCanaryResponse
The HouseCanaryResponse object encapsulates an HTTP response from the HouseCanary API.

###### Properties:
- **endpoint_name** - Gets the endpoint name of the original request
- **response** - Gets the underlying response object.
###### Methods:
- **json()** - Gets the body of the response from the API as json.
- **has_property_error()** - Returns true if any requested address had a business logic error, otherwise returns false.
- **get_business_error_messages()** - Gets a list of business error message strings for each of the requested properties that had a business error. If there was no error, returns an empty list.
- **hc_properties()** - Gets a list of HouseCanaryProperty objects for the requested properties, each containing the property's returned json data from the API.

### HouseCanaryProperty
The HouseCanaryProperty represents a single address and it's returned data.

###### Properties:
- **address**
- **zipcode**
- **zipcode_plus4**
- **address_full**
- **city**
- **country_fips**
- **lat**
- **lng**
- **state**
- **unit**
- **meta**
- **api_code**
- **api_code_description**
- **json_results**

###### Methods:
- **has_property_error()** - Returns boolean of whether there was a business logic error fetching data for this property.
- **get_property_error()** - If there was a business error fetching data for this property, returns the error message.

###### Example:
```python
hc_response = client.property.score(("82 County Line Rd", "72173", "meta information"))
p = result.hc_properties()[0]
print p.address
# "82 County Line Rd"
print p.zipcode
# "72173"
print p.meta
# "meta information"
print p.json_results
# {u'property_score_description': u'medium', u'property_score': 75}
```
