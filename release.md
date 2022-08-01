# Create a new release

### Step 1) Push code

Make changes, commit and push. The build workflow starts automatically and builds the Docker image and wheels. The Docker image is automatically pushed to Dockerhub. The wheels need to be manually uploaded to PyPI as explained below.

### Step 2) Bump version

Bump the version in `setup.py`

### Step 2) Create tag and release

Now, create a tag with the same version just entered in the `setup.py` and push that tag to the remote.
```
git tag vx.x.x
git push origin vx.x.x
```

Then create a release on GitHub using this tag.

### Step 3) Upload wheels to PyPI

First, make sure you have the most recent version of twine installed on the host
```
python3 -m pip install --upgrade twine
```

Then, download the wheels from the (successfully completed) workflow run. Place them inside the "dist" folder (create if it does not exist). Then, upload to PyPI with
```
python3 -m twine upload dist/*
```

#### Step 4) Tag Docker image with correct version 

When pushing changes, a Docker image `lubo1994/mv-extractor:dev` is being build and pushed to DockerHub. Upon a release, this image should be tagged with the correct release version and the `latest` tag. To this end, first pull the `dev` image
```
sudo docker pull lubo1994/mv-extractor:dev
```
and then tag and push it as follows
```
sudo docker tag lubo1994/mv-extractor:dev lubo1994/mv-extractor:vx.x.x
sudo docker push lubo1994/mv-extractor:vx.x.x
sudo docker tag lubo1994/mv-extractor:vx.x.x lubo1994/mv-extractor:latest
sudo docker push lubo1994/mv-extractor:latest
```
where `vx.x.x` is replaced with the version of the release.