### Create a new release

#### Create tag and release

```
git tag vx.x.x
git push origin vx.x.x
```

Then create a release on GitHub using this tag.

#### Build and push Docker image

```
sudo docker build . --tag=lubo1994/mv-extractor:vx.x.x
sudo docker tag lubo1994/mv-extractor:vx.x.x lubo1994/mv-extractor:latest
sudo docker push lubo1994/mv-extractor:vx.x.x
sudo docker push lubo1994/mv-extractor:latest
```