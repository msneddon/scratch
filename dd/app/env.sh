#! /bin/bash

export DEEPDIVE_HOME=`cd $(dirname $0)/../../deepdive; pwd`
export APP_HOME=`pwd`

# Machine Configuration
export MEMORY="4g"
export PARALLELISM=2

# Database Configuration
export DBNAME=chemotaxis
export PGUSER=${PGUSER:-`whoami`}
export PGPASSWORD=${PGPASSWORD:-}
export PGPORT=${PGPORT:-5432}
export PGHOST=${PGHOST:-localhost}

# SBT Options
export SBT_OPTS="-Xmx$MEMORY"
export JAVA_OPTS="-Xmx$MEMORY"