# PII Masking for the LLM POC


Small POC for the masking of the PII data that is being send to the LLMs.
Detecting PII is not a trivial task, therefore this solution is pretty naive and will not support any real world use cases.
I am using some basic regex checks for the universally recognizable data, such as: email, international phone number.
For user names and organization names i used [spacy](https://github.com/explosion/spaCy) library, which uses NLP models to recognize data.

LLM API used is Hugging Face [Inference API](https://huggingface.co/inference-api/serverless). Its free to use and open source.

Code is divided into 3 modules: api - containing core logic, schema - pydantic schemas for request and response, tests - unit tests for the app. This might be overkill for such a small app but i like to have proper structure anyway.

## Setting up env variables
There are 2 environmental variables, in order to set them you need to edit `docker-compose.yml` file.

`HUGGINGFACE_TOKEN` - you need to have huggingface token in order to use any LLM model provided by the ineference api. You can generate it by creating account on huggingface.com and going to the settings.
`HUGGINGFACE_MODEL` - LLM model used. By default its `Llama-3.2-11B-Vision-Instruct`, which is relatively big and slow. You can experiment with different models. List of supported models - https://huggingface.co/models?inference=warm&sort=trending

## Running locally
To run this locally you need to have docker engine installed with docker compose.

command:
`docker compose up`

## Unit tests
Code is covered by unit tests.

command:
`docker compose run web pytest`
