#!/usr/bin/env bash

sh build.sh

docker run --rm --gpus=all --name uq_fhir_cxrmate_api --publish 80:80 uq_fhir_cxrmate_api
