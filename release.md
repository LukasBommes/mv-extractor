# Create a new release

### Step 1) Push code

Make changes, commit and push. The build workflow starts automatically and builds the Docker image and wheels. The Docker image is automatically pushed to Dockerhub. The wheels need to be manually uploaded to PyPI as explained below.

### Step 2) Bump version

Bump the version in `version.txt`

### Step 2) Create tag and release

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

#### Step 4) Rename Docker image 



```
sudo docker build . --tag=lubo1994/mv-extractor:vx.x.x
sudo docker tag lubo1994/mv-extractor:vx.x.x lubo1994/mv-extractor:latest
sudo docker push lubo1994/mv-extractor:vx.x.x
sudo docker push lubo1994/mv-extractor:latest
```