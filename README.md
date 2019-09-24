# Telstra Messaging Qt App

A little app to send and receive messages using the [Telstra Messaging API](https://www.telstra.com.au/business-enterprise/solutions/mobility-solutions/mobile-messaging/messaging-api) (Australia).

![](screenshot.png)

## Dependencies
- PyQt5
- requests

## Usage
1. Make an account on the [dev portal](https://dev.telstra.com/). 
2. Create a free trial app, and copy the key and secret.
3. Create a file `app.conf` in the same directory as `telstrasmsqt.py`, format it as follows:
```
[keys]
key1_here secret1_here
key2_here secret2_here
...
```
4. Run the app `python3 telstrasmsqt.py`.

## Other
Please report bugs or feature requests via Github issues. Contributions are welcome.