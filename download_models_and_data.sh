MODEL_DIR=models
DATA_DIR=data
MODEL=${1:-uncased}

mkdir -p $MODEL_DIR
mkdir -p $DATA_DIR

wget https://bootleg-data.s3-us-west-2.amazonaws.com/models/latest/bootleg_$MODEL.tar.gz -P $MODEL_DIR
wget https://bootleg-data.s3-us-west-2.amazonaws.com/data/latest/entity_db.tar.gz -P $DATA_DIR

tar -xzvf $MODEL_DIR/bootleg_$MODEL.tar.gz -C $MODEL_DIR
tar -xzvf $DATA_DIR/entity_db.tar.gz -C $DATA_DIR
