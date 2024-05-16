# SEIR Markov Lockdown

Markov SEIR model with lockdown.

![demo](./examples/simple/result_simple.gif)

## Installation

- Python version: ^3.9

```sh
pip install git+https://github.com/jjj999/SEIR-Markov-lockdown.git
```

## Usage

1. Copy the template files:
   1. [config.yaml](./examples/template/config.yaml): Config file for plotting.
   2. [cities.csv](./examples/template/cities.csv): Definition of cities.
   3. [connections.csv](./examples/template/connections.csv): Definition of city connections.
   4. [city_groups.csv](./examples/template/city_groups.csv): Definition of city groups.
   5. [people.csv](./examples/template/people.csv): Definition of people.
2. Run simulation:
  ```sh
  cd /path/to/folder/   # if needed
  python -m seir_markov_lockdown config.yaml
  ```

## Examples

- [simple](./examples/simple/): Example with the simple definitions.
