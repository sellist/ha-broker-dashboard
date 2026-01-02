- Home Assistant Monitoring Dashboard
- Goals
    - Provide realtime dashboard of sensors pushing to MQTT broker
    - Should all run within a docker container
    - topics and implementation should be defined by config file
      - i.e., in a yaml file, a line should be:
        ```- TOPIC NAME
            type: str
            name: str
            implementation: str
            history: int
            ```
        ```
        - TOPIC NAME: the MQTT topic to subscribe to
        - type: sensor type (e.g., temperature, humidity, motion)
        - name: sensor name to show on dashboard
        - implementation: how to serve the data to frontend (e.g., gauge, graph, text)
        - history: how many iterations of data to keep for graphing (messages)

- program start:
  - connect to mqtt broker
  - setup web server
  - read config file
  - subscribe to topics
  - start listening for messages
  - on message received:
    - parse message
    - update data structure
    - if implementation is graph, append to history
    - update frontend via websocket
    - repeat

- Frontend:
-  - simple web page
  - use websockets to receive updates
  - for each sensor, create appropriate visualization based on implementation
  - update visualizations in realtime as data is received


        
        