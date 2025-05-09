## Functions

Timer function (button to start and display)

Notifications 24 hours after clothes were hung out 

Live camera feed 

Notifications for upcoming weather events 

Manual override button 

Current status display (cover up or down)

//

## Content

This is the front-end dashboard for our IoT smart clothes drying rack.  

The page is built with plain HTML, CSS, and JavaScript.  

It connects to a Flask backend and Raspberry Pi to show real-time data and control the cover.

## Functions included in the web front end

1.Displaying live camera feed (`/video_feed`)

2.Showing real-time rack and weather status via `/api/status`:

  - Cover state: extended / retracted

  - Sunlight intensity (lux)

  - Rain detection status

  - Simple weather icon

3.Control buttons (POST to `/api/control`):

  - Extend / Retract cover

  - Start / Reset drying timer

  - Emergency manual close

4.Notification system:

  - Rain expected in 3 hours (Customizable)

  - (No rain expected in the next 12 hours – suitable for drying)

---

## API Integration (for backend)


1.Get Status

### `GET /api/status`  

Called every 5 seconds to update the display.

Sample response:

```json

{
  "coverExtended": true,

  "sunlight": 150,

  "rainDetected": false,

  "weatherCondition": "sunny",

  "rainExpected": false,

  "rainHours": 0

}
```

2.Cover Control

### `POST /api/control`  

Sends a control command:

```json

{ "command": "up|down|manualClose" }  

```

Expected response:

```json

{ "success": true }

```

3.camera video

### `GET /video_feed`  

Returns MJPEG stream from Raspberry Pi camera.


## File Structure


- `index.html`: Contains all layout, styling, and interaction logic

  - No frameworks used (pure static HTML/JS)

  - Buttons use `fetch()` to talk to the backend

  - Timer is implemented with `setInterval()`


## Note

This file is about the front-end layout and logic for this version.  

Each feature is modular and can be tweaked based on our feedback.

> I'm happy to adjust layout/styling if needed.  


## Frontend & UI 


UI Design Principles

Theme:  Milky white & yellow color (maybe) clean, fresh look

Layout: Modular, card-style layout

Technology:

Pure HTML, CSS, and JavaScript

Performance: fast-loading for Raspberry Pi hosting.


+------------------------------------------------------------+

| Smart Clothes Drying Rack Dashboard                        |

+------------------------------------------------------------+

| 📸 Live Camera Feed:                                       |

|   [🔴 Live Stream Video Window Here]                       |

|   - Source: Raspberry Pi camera                            |

|   - Route: /video                                          |

|   - Top-left section                                       |

+------------------------------------------------------------+

| 📊 Current Status                                          |

|   [ Start Timer ]                                          |

|   - Cover State: "Extended" or "Retracted"                 |

|   - Sunlight: in lux (e.g., `350 lux`)                     |

|   - Rain Detection: "Rain Detected" or "No Rain"           |

|   - Weather: simple icon (☀️, ☁️, ☔️)                       |

|   - Backend: GET /api/status                               |

|   - Data from sensors via Raspberry Pi                     |

+------------------------------------------------------------+

| ⏲️ Drying Timer                                             |

|   [Extend cover]   [Retract Cover]   [Start Timer]  [Reset] |

| - Buttons to extend/retract cover                           |

| - Start/reset drying timer                                  |

| - Manual override button labeled "Manual Close"             |

| - Timer display (hh:mm:ss)                                  |

| - Last manual control time                                  |

| - Backend: POST /api/control                                |

|     { "command": "up" | "down" | "override" }               |

+------------------------------------------------------------+

| 🛎️ Notifications                                            |

|   - Just 2 Weather alert:                                   |                                        

|   • "Rain expected in 3 hours ☔️"                           |

|   • "No rain expected in the next 12 hours ☀️"              |

+------------------------------------------------------------+



