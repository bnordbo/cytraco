#!/usr/bin/env bash

set -e

id=$(git log --oneline -1 | cut -d' ' -f1)
pr=$(git log --oneline -1 | cut -d' ' -f5 | tr -d \#)
id="$id-pr-$pr"

mkdir -p reports/$id
interrogate -v > reports/$id/docs.out
radon cc -sn A . > reports/$id/cc.out
radon mi -sn A . > reports/$id/cc.mi
radon raw -s . > reports/$id/cc.raw
radon hal . > reports/$id/cc.hal
