# Land-Slide

# Installation

### Land-Slide

- How to build using docker-compose

  ```bash
  docker-compose build
  ```

- How to run using docker-compose
  ```bash
  docker-compose up
  ```

### if got error like "The requested image's platform (linux/amd64) does not match the detected host platform"

please add this line in yaml service

```bash
  platform: linux/amd64
```
"# flood_predict" 
