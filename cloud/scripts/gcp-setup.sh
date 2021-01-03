# script variables
PROJECT_ID="euro-lotto-manager-tes" # Project IDs must be between 6 and 30 characters.
REGION="europe-west2"  # europe-west2 is London
BUCKET_NAME="results-${PROJECT_ID}"


echo "*** STEP 1: Requesting for Authentication ***"
echo
gcloud auth login


echo
echo "*** STEP 2: Creating Project ***"
echo
gcloud projects create ${PROJECT_ID}

PROJECT_NUMBER=`gcloud projects list --filter=${PROJECT_ID} --format="value(PROJECT_NUMBER)"`

echo
echo "*** STEP 3: Selecting Project ***"
echo
gcloud config set project ${PROJECT_ID}


echo
echo "*** INFO 4 Creating buckets ***"
echo
gsutil mb -c standard -l ${REGION} gs://${BUCKET_NAME}  # Where results will be stored