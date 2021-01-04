#!/bin/bash
set -e # if error exit

if [[ $# -eq 0 ]] ; then
    echo 'You must provide a branch name as the only argument'
    exit 0
fi

# script variables
PROJECT_ID="euro-lotto-manager-$1" # Project IDs must be between 6 and 30 characters.
REGION="europe-west2"  # europe-west2 is London
BUCKET_NAME="results-${PROJECT_ID}"

# Check BILLING_ACCOUNT_ID is set
if [ -n "${BILLING_ACCOUNT_ID}" ]; then
    echo
    echo "Using BILLING_ACCOUNT_ID environment variable."
    echo
else
    echo
    echo "*** ERROR ***"
    echo "Please set BILLING_ACCOUNT_ID environment variable."
    echo "You can find it here: https://console.cloud.google.com/billing"
    echo "Exiting..."
    echo
    exit
fi


echo "*** STEP 1/9: Requesting for Authentication ***"
echo
gcloud auth login


echo
echo "*** STEP 2/9: Creating Project ***"
echo
gcloud projects create ${PROJECT_ID}

PROJECT_NUMBER=`gcloud projects list --filter=${PROJECT_ID} --format="value(PROJECT_NUMBER)"`

echo
echo "*** STEP 3/9: Link Project to billing account ***"
echo
gcloud alpha billing projects link ${PROJECT_ID} \
    --billing-account ${BILLING_ACCOUNT_ID}

echo
echo "*** STEP 4/9: Selecting Project ***"
echo
gcloud config set project ${PROJECT_ID}


echo
echo "*** STEP 5/9: Enabling GCP APIs ***"
echo
gcloud services enable cloudtrace.googleapis.com            # Cloud Trace API
gcloud services enable logging.googleapis.com               # Cloud Logging API
gcloud services enable compute.googleapis.com               # general compute resources needed for functions
gcloud services enable cloudresourcemanager.googleapis.com  # access GCP resource metadata (e.g. permissions)
gcloud services enable cloudbuild.googleapis.com            # github triggers
gcloud services enable cloudfunctions.googleapis.com        # cloud functions
gcloud services enable cloudscheduler.googleapis.com        # cloud scheduler (crontab for cloud)
gcloud services enable appengine.googleapis.com             # appengine needed for cloud scheduler


echo
echo "*** STEP 6/9: 60s delay - allow APIs to enable ***"
echo
sleep 60


echo
echo "*** STEP 7/9 Creating buckets ***"
echo
gsutil mb -c standard -l ${REGION} gs://${BUCKET_NAME}  # Where results will be stored


echo
echo "*** STEP 8/9 Adding permissions"
echo
# note gcf-admin-robot = Google Cloud Functions Service Agent
# and PROJECT_ID@appspot.gserviceaccount.com is App engine default service account:
# See https://cloud.google.com/functions/docs/concepts/iam#access_control_for_service_accounts

echo "Permitting cloud build to deploy functions"
gcloud projects add-iam-policy-binding ${PROJECT_ID}@appspot.gserviceaccount.com \
    --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
    --role=roles/cloudfunctions.developer

echo
echo "Permitting deploy build rule to upload function source code"
gcloud projects add-iam-policy-binding ${PROJECT_ID}@appspot.gserviceaccount.com \
    --member=serviceAccount:service-${PROJECT_NUMBER}@gcf-admin-robot.iam.gserviceaccount.com \
    --role=roles/storage.objectCreator

echo
echo "Permitting deployment of functions from trigger"
gcloud iam service-accounts add-iam-policy-binding ${PROJECT_ID}@appspot.gserviceaccount.com \
    --member=serviceAccount:service-${PROJECT_NUMBER}@gcf-admin-robot.iam.gserviceaccount.com \
    --role=roles/iam.serviceAccountUser

echo
echo "Permitting deployment of functions from trigger"
gcloud iam service-accounts add-iam-policy-binding ${PROJECT_ID}@appspot.gserviceaccount.com \
    --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
    --role=roles/iam.serviceAccountUser

echo
echo "Permitting function service account to invoke other functions"
gcloud projects add-iam-policy-binding ${PROJECT_ID}@appspot.gserviceaccount.com \
    --member=serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com  \
    --role=roles/cloudfunctions.invoker

echo
echo "Permitting function service account to read from storage"
gcloud projects add-iam-policy-binding ${PROJECT_ID}@appspot.gserviceaccount.com \
    --member=serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com  \
    --role=roles/storage.objectViewer

echo
echo "Permitting function service account to write to storage"
gcloud projects add-iam-policy-binding ${PROJECT_ID}@appspot.gserviceaccount.com \
    --member=serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com  \
    --role=roles/storage.objectCreator


echo
echo "*** STEP 9/9 Creating Cloud Scheduler and Topic ***"
echo
# Have to create an app engine app in order to use scheduler
gcloud app create --project=${PROJECT_ID} --region=${REGION}
gcloud pubsub topics create scheduled-weekly-9am
# schedule is crontab format, see: https://crontab.guru/#0_9_*_*_6
gcloud scheduler jobs create pubsub weekly-9am --schedule="0 9 * * 6" \
    --topic=scheduled-weekly-9am --message-body="Its 9am Saturday, time to work!"
