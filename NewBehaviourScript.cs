using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

[System.Serializable]
class MyCar
{
    public int x;
    public int y;

    override public string ToString()
    {
        return "X: " + x + ", Y: " + y;
    }
}

public class NewBehaviourScript : MonoBehaviour
{
    string simulationURL = null;
    private float waitTime = 2.0f;
    private float timer = 0.0f;

    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(ConnectToMesa());
    }

    IEnumerator ConnectToMesa()
    {
        WWWForm form = new WWWForm();

        using (UnityWebRequest www = UnityWebRequest.Post("http://localhost:5000/games", form))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.Log(www.error);
            }
            else
            {
                simulationURL = www.GetResponseHeader("Location");
                Debug.Log("Connected to simulation through Web API");
                Debug.Log(simulationURL);
            }
        }
    }

    IEnumerator UpdatePositions()
    {
        using (UnityWebRequest www = UnityWebRequest.Get(simulationURL))
        {
            if (simulationURL != null)
            {
                // Request and wait for the desired page.
                yield return www.SendWebRequest();

                Debug.Log(www.downloadHandler.text);
                Debug.Log("Data has been processed");
                MyCar cars = JsonUtility.FromJson<MyCar>(www.downloadHandler.text);
                Debug.Log(cars.ToString());

                transform.position = new Vector3(0, cars.x, cars.y);
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
        timer += Time.deltaTime;
        if (timer > waitTime)
        {
            StartCoroutine(UpdatePositions());
            timer = timer - waitTime;
        }
    }
}
