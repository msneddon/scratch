##################################################################################
#
# 
#
#

SERVICE = rxn_net_dynamics

SERVICE_NAME = KBaseRxnNetDynamics
SERVICE_PORT = 7047
THREADPOOL_SIZE = 20
MEMORY = 1000
MAX_MEMORY = 4000

BNG_DIR_NAME = BioNetGen-2.2.5-stable

##################################################################################
#Additional configuration variables which are pulled from the environment
DEPLOY_RUNTIME ?= /kb/runtime
TARGET ?= /kb/deployment

GLASSFISH_HOME ?= $(DEPLOY_RUNTIME)/glassfish3
ASADMIN = $(GLASSFISH_HOME)/glassfish/bin/asadmin

TOP_DIR = $(shell python -c "import os.path as p; print p.abspath('../..')")
TOP_DIR_NAME = $(shell basename $(TOP_DIR))
DIR = $(shell pwd)

#set the BNG root location
LOCAL_BNGPATH = $(DIR)/lib/bng/$(BNG_DIR_NAME)
DEPLOYED_BNGPATH = $(TARGET)/lib/bng/$(BNG_DIR_NAME)

# mark the commit and tag we are on for tracking deployments
GITCOMMIT := $(shell git rev-parse --short HEAD)
TAGS := $(shell git tag --contains $(GITCOMMIT))

# including the common makefile gives us a handle to the service directory
include $(TOP_DIR)/tools/Makefile.common
$(SERVICE_DIR) ?= /kb/deployment/services/$(SERVICE)

.PHONY : test

##################################################################################
# targets for compiling the service client/server code and docs
default: all

all: bng bng-wrapper compile-typespec build-docs

setup-dirs:
	mkdir -p lib/biokbase/$(SERVICE_NAME)
	mkdir -p lib/javascript/$(SERVICE_NAME)

compile-typespec: setup-dirs
	compile_typespec \
		--client Bio::KBase::$(SERVICE_NAME)::Client \
		--py biokbase/$(SERVICE_NAME)/Client \
		--js javascript/$(SERVICE_NAME)/Client \
		--url https://kbase.us/services/trees \
		$(SERVICE_NAME).spec lib
	rm -f lib/KBaseTrees*.py
	rm -f lib/KBaseTrees*.pm

build-java-classes:
	gen_java_types -s src/java/ -S $(SERVICE_NAME).spec

build-docs: compile-typespec
	mkdir -p docs
	pod2html --infile=lib/Bio/KBase/$(SERVICE_NAME)/Client.pm --outfile=docs/$(SERVICE_NAME).html
	rm -f pod2htmd.tmp

##################################################################################
# targets for building and deploying BioNetGen
bng: $(LOCAL_BNGPATH)/bin/run_network

# todo: write the proper dependency so that we rebuild if we edit BNG - although not
# needed yet since we should not be editing and BNG source in this repo....
$(LOCAL_BNGPATH)/bin/run_network:
	cd $(LOCAL_BNGPATH);\
	export BNGPATH=$(LOCAL_BNGPATH);\
	cd Network3;\
	./configure --disable-shared --prefix=$(LOCAL_BNGPATH);\
	make;\
	make install;

bng-wrapper: bng
	echo "#!/bin/sh" > lib/bng/BNG2
	echo "export BNGPATH=$(LOCAL_BNGPATH)" >> lib/bng/BNG2
	echo "$(DEPLOY_RUNTIME)/bin/perl $(LOCAL_BNGPATH)/BNG2.pl \"\$$@\"" >> lib/bng/BNG2
	chmod +x lib/bng/BNG2
	cp -v lib/bng/BNG2 $(TOP_DIR)/bin/.

clean-bng:
	cd $(LOCAL_BNGPATH);\
	rm -fv bin/*;\
	cd Network3;\
	make clean;

deploy-bng:
	rsync -avz --delete lib/bng $(TARGET)/lib/
	echo "#!/bin/sh" > lib/bng/BNG2
	echo "export BNGPATH=$(DEPLOYED_BNGPATH)" >> lib/bng/BNG2
	echo "$(DEPLOY_RUNTIME)/bin/perl $(DEPLOYED_BNGPATH)/BNG2.pl \"\$$@\"" >> lib/bng/BNG2
	chmod +x lib/bng/BNG2
	cp -v lib/bng/BNG2 $(TARGET)/bin/.

##################################################################################
# here are the standard KBase test targets (test, test-all, deploy-client, deploy-scripts, & deploy-service)
test: test-all

test-all:  test-service test-client test-scripts

test-client:
	#prove test/perl-tests/testBasicResponses.t  || (echo "NOTE: Tests require the Tree service is running at localhost:7047" && false)
	#prove test/perl-tests/testIntrospectionMethods.t
	#prove test/perl-tests/testQueryMethods.t

test-scripts:
	#prove test/perl-tests/testBasicScriptResponses.t || (echo "NOTE: Tests require the Tree service is running at localhost:7047" && false)

test-service:
	#prove test/perl-tests/testServerUp.t || (echo "NOTE: Tests require the Tree service is running at localhost:7047" && false)

test-bng:
	BNG2 --version



##################################################################################
# here are the standard KBase deployment targets (deploy, deploy-all, deploy-client, deploy-scripts, & deploy-service)
deploy: deploy-all

deploy-all: deploy-client deploy-service deploy-scripts deploy-docs
	echo "OK... Done deploying ALL artifacts (includes clients, docs, scripts and service) of $(SERVICE)."
	
deploy-client:
	mkdir -p $(TARGET)/lib/Bio/KBase/$(SERVICE_NAME)
	mkdir -p $(TARGET)/lib/biokbase/$(SERVICE_NAME)
	mkdir -p $(TARGET)/lib/javascript/$(SERVICE_NAME)
	touch lib/biokbase/__init__.py #do not include code in biokbase/__init__.py
	touch lib/biokbase/$(SERVICE_NAME)/__init__.py
	cp lib/Bio/KBase/$(SERVICE_NAME)/Client.pm $(TARGET)/lib/Bio/KBase/$(SERVICE_NAME)/.
	cp lib/Bio/KBase/$(SERVICE_NAME)/Util.pm $(TARGET)/lib/Bio/KBase/$(SERVICE_NAME)/.
	cp lib/biokbase/$(SERVICE_NAME)/* $(TARGET)/lib/biokbase/$(SERVICE_NAME)/.
	cp lib/javascript/$(SERVICE_NAME)/* $(TARGET)/lib/javascript/$(SERVICE_NAME)/.
	-cp dist/KBaseTrees.jar $(TARGET)/lib/.
	echo "deployed clients of $(SERVICE)."
	
## perl script directory and local dev container bin directory
BIN_DIR = $(TOP_DIR)/bin
SRC_PERL = $(wildcard scripts/*.pl)
BIN_PERL = $(addprefix $(BIN_DIR)/,$(basename $(notdir $(SRC_PERL))))

deploy-scripts:
	export KB_TOP=$(TARGET); \
	export KB_RUNTIME=$(DEPLOY_RUNTIME); \
	export KB_PERL_PATH=$(TARGET)/lib bash ; \
	for src in $(SRC_PERL) ; do \
		basefile=`basename $$src`; \
		base=`basename $$src .pl`; \
		echo install $$src $$base ; \
		cp $$src $(TARGET)/plbin ; \
		$(WRAP_PERL_SCRIPT) "$(TARGET)/plbin/$$basefile" $(TARGET)/bin/$$base ; \
	done

deploy-scripts-to-dev-container: $(BIN_PERL)

$(BIN_DIR)/%: scripts/%.pl $(TOP_DIR)/user-env.sh
	$(WRAP_PERL_SCRIPT) '$$KB_TOP/modules/$(CURRENT_DIR)/$<' $@

## NOTE: next target assume you have the api-mods-aug2013 branch of dev container, which
## has not been officially accepted....
deploy-scripts-nice:
	$(TOOLS_DIR)/deploy-wrappers \
		--jsonCommandsFile COMMANDS.json \
		--target $(TARGET) \
		--devContainerToolsDir $(TOOLS_DIR)

deploy-docs:
	mkdir -p $(SERVICE_DIR)/webroot
	cp docs/*.html $(SERVICE_DIR)/webroot/.


# deploys all libraries and scripts needed to start/stop the service
deploy-service: deploy-java-service deploy-service-start_scripts

prepare-deploy-target:
	mkdir -p $(TARGET)/lib/Bio/KBase/$(PERL_SERVICE_NAME)
	mkdir -p $(TARGET)/lib/Bio/KBase/$(SERVICE_NAME)
	mkdir -p $(SERVICE_DIR)
	mkdir -p $(SERVICE_DIR)/log
	cp deploy.cfg $(SERVICE_DIR)/.
	echo $(GITCOMMIT) > $(SERVICE_DIR)/$(SERVICE).serverdist
	echo $(TAGS) >> $(SERVICE_DIR)/$(SERVICE).serverdist

#deploys the java service only (without start/stop scripts)
deploy-java-service: cpp-lib deploy-perl-service prepare-deploy-target
	ant -Djarsdir=../jars/lib/jars -Ddeploycfg=$(SERVICE_DIR)/deploy.cfg
	cp dist/KBaseTreesService.war $(SERVICE_DIR)/.
	cp lib/libKBTreeUtil.* $(TARGET)/lib/.

#deploys the internal perl service only (without start/stop scripts)
deploy-perl-service: cpp-lib prepare-deploy-target
	cp lib/Bio/KBase/$(PERL_SERVICE_NAME)/Service.pm $(TARGET)/lib/Bio/KBase/$(PERL_SERVICE_NAME)/.
	cp lib/Bio/KBase/$(PERL_SERVICE_NAME)/$(PERL_SERVICE_NAME)Impl.pm $(TARGET)/lib/Bio/KBase/$(PERL_SERVICE_NAME)/.
	cp lib/$(PERL_SERVICE_PSGI_FILE) $(TARGET)/lib/.
	cp lib/KBTree_cpp_lib/lib/perl_interface/Bio/KBase/$(PERL_SERVICE_NAME)/TreeCppUtil.pm $(TARGET)/lib/Bio/KBase/$(PERL_SERVICE_NAME)/.
	cp lib/KBTree_cpp_lib/lib/perl_interface/TreeCppUtil.* $(TARGET)/lib/.
	cp lib/Bio/KBase/$(PERL_SERVICE_NAME)/Util.pm $(TARGET)/lib/Bio/KBase/$(PERL_SERVICE_NAME)/.
	cp lib/Bio/KBase/$(PERL_SERVICE_NAME)/Community.pm $(TARGET)/lib/Bio/KBase/$(PERL_SERVICE_NAME)/.

# creates start/stop scripts and copies them to the deployment target
deploy-service-start_scripts: build-service-start-stop-scripts
	cp service/* $(SERVICE_DIR)/.

build-service-start-stop-scripts: build-perl-service-start-stop-scripts
	mkdir -pv service
	echo '#!/bin/sh' > ./service/start_service
	echo "./start_perl_service" >> ./service/start_service
	echo "export KB_DEPLOYMENT_CONFIG=$(SERVICE_DIR)/deployment.cfg" >> ./service/start_service
	echo "$(SERVICE_DIR)/glassfish_administer_service.py --admin $(ASADMIN)\
	 --domain $(SERVICE_NAME) --domain-dir $(SERVICE_DIR)/glassfish_domain\
	 --war $(SERVICE_DIR)/KBaseTreesService.war --port $(SERVICE_PORT)\
	 --threads $(THREADPOOL_SIZE) --Xms $(MEMORY) --Xmx $(MAX_MEMORY)\
	 --noparallelgc --properties KB_DEPLOYMENT_CONFIG=\$$KB_DEPLOYMENT_CONFIG"\
	 >> ./service/start_service
	echo '#!/bin/sh' > ./service/stop_service
	echo "./stop_perl_service" >> ./service/stop_service
	echo "$(SERVICE_DIR)/glassfish_administer_service.py --admin $(ASADMIN)\
	 --domain $(SERVICE_NAME) --domain-dir $(SERVICE_DIR)/glassfish_domain\
	 --port $(SERVICE_PORT)" >> ./service/stop_service
	echo '#!/bin/sh' > ./service/stop_domain
	echo "$(ASADMIN) stop-domain --domaindir $(SERVICE_DIR)/glassfish_domain $(SERVICE_NAME)"\
	 >> ./service/stop_domain
	chmod +x service/start_service service/stop_service service/stop_domain

build-perl-service-start-stop-scripts:
	# First create the start script (should be a better way to do this...)
	echo '#!/bin/sh' > ./start_perl_service
	echo "echo starting $(SERVICE) service." >> ./start_perl_service
	echo 'export PERL5LIB=$$PERL5LIB:$(TARGET)/lib' >> ./start_perl_service
	echo "export FILE_TYPE_DEF_FILE=$(FILE_TYPE_DEF_FILE)" >> ./start_perl_service
	echo "export TREE_DEPLOYMENT_CONFIG=$(SERVICE_DIR)/deploy.cfg" >> ./start_perl_service
	echo "export TREE_DEPLOYMENT_SERVICE_NAME=$(SERVICE)" >> ./start_perl_service
	echo "$(DEPLOY_RUNTIME)/bin/starman --listen :$(PERL_SERVICE_PORT) --pid $(PID_FILE) --daemonize \\" >> ./start_perl_service
	echo "  --access-log $(ACCESS_LOG_FILE) \\" >>./start_perl_service
	echo "  --error-log $(ERR_LOG_FILE) \\" >> ./start_perl_service
	echo "  $(TARGET)/lib/$(PERL_SERVICE_PSGI_FILE)" >> ./start_perl_service
	echo "echo $(SERVICE_NAME) service is listening on port $(PERL_SERVICE_PORT).\n" >> ./start_perl_service
	# Second, create a debug start script that is not daemonized
	echo '#!/bin/sh' > ./debug_start_perl_service
	echo 'export PERL5LIB=$$PERL5LIB:$(TARGET)/lib' >> ./debug_start_perl_service
	echo 'export STARMAN_DEBUG=1' >> ./debug_start_perl_service
	echo "export TREE_DEPLOYMENT_CONFIG=$(SERVICE_DIR)/deploy.cfg" >> ./debug_start_perl_service
	echo "export TREE_DEPLOYMENT_SERVICE_NAME=$(SERVICE)" >> ./debug_start_perl_service
	echo "$(DEPLOY_RUNTIME)/bin/starman --listen :$(PERL_SERVICE_PORT) --workers 1 \\" >> ./debug_start_perl_service
	echo "    $(TARGET)/lib/$(PERL_SERVICE_PSGI_FILE)" >> ./debug_start_perl_service
	# Third create the stop script
	echo '#!/bin/sh' > ./stop_perl_service
	echo "echo trying to stop $(SERVICE) service." >> ./stop_perl_service
	echo "pid_file=$(PID_FILE)" >> ./stop_perl_service
	echo "if [ ! -f \$$pid_file ] ; then " >> ./stop_perl_service
	echo "\techo \"No pid file: \$$pid_file found for service $(SERVICE_NAME).\"\n\texit 1\nfi" >> ./stop_perl_service
	echo "pid=\$$(cat \$$pid_file)\nkill \$$pid\n" >> ./stop_perl_service
	chmod +x start_perl_service stop_perl_service debug_start_perl_service
	mkdir -pv service
	mv -f start_perl_service service/start_perl_service
	mv -f debug_start_perl_service service/debug_start_perl_service
	mv -f stop_perl_service service/stop_perl_service



# this undeploy target is a custom hack for Trees
undeploy: undeploy-script-wrappers
	#undeploy standard stuff
	rm -rfv $(SERVICE_DIR)
	rm -rfv $(TARGET)/lib/Bio/KBase/$(SERVICE_NAME)
	rm -rfv $(TARGET)/lib/$(SERVICE_PSGI_FILE)
	rm -rfv $(TARGET)/lib/biokbase/$(SERVICE_NAME)
	rm -rfv $(TARGET)/lib/javascript/$(SERVICE_NAME)
	#undeploy custom libs
	rm -rfv $(TARGET)/lib/TreeCppUtil.so
	rm -fv  $(TARGET)/lib/forester_1005.jar
	echo "OK ... Removed all deployed files."

undeploy-script-wrappers:
	$(TOOLS_DIR)/deploy-wrappers \
		--jsonCommandsFile COMMANDS.json \
		--target $(TARGET) \
		--devContainerToolsDir $(TOOLS_DIR) \
		--undeploy


# remove files generated within this directory and dev_container/bin
cleanarg:
	cd lib/KBTree_cpp_lib; make clean DEPLOY_RUNTIME=$(DEPLOY_RUNTIME);
	rm -f lib/Bio/KBase/$(SERVICE_NAME)/Client.pm
	rm -f lib/$(PERL_SERVICE_PSGI_FILE)
	rm -rf lib/biokbase
	rm -rf lib/javascript
	rm -rf docs
	rm -rf dist
	rm -rf classes
	rm -f service/start_service service/stop_service
	rm -f service/start_perl_service service/stop_perl_service service/debug_start_perl_service

clean-dev-container-script-wrappers:
	$(TOOLS_DIR)/deploy-wrappers \
		--jsonCommandsFile COMMANDS.json \
		--target $(TOP_DIR) \
		--no-copyScripts \
		--devContainerToolsDir $(TOOLS_DIR) \
		--undeploy