using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

public static class JsonHelper
{
    public static T[] FromJson<T>(string json)
    {
        Wrapper<T> wrapper = JsonUtility.FromJson<Wrapper<T>>(json);
        return wrapper.Items;
    }

    public static string ToJson<T>(T[] array)
    {
        Wrapper<T> wrapper = new Wrapper<T>();
        wrapper.Items = array;
        return JsonUtility.ToJson(wrapper);
    }

    public static string ToJson<T>(T[] array, bool prettyPrint)
    {
        Wrapper<T> wrapper = new Wrapper<T>();
        wrapper.Items = array;
        return JsonUtility.ToJson(wrapper, prettyPrint);
    }

    [System.Serializable]
    private class Wrapper<T>
    {
        public T[] Items;
    }
}


[System.Serializable]
class Agent
{
    public int x;
    public int y;
    public string tipo;
    public int cajasActualesRobot;
    public bool limpio;
    public int stackAsignadoX;
    public int stackAsignadoY;
    public bool leavedBoxes;
    public int inStack;
    public int boxesInStack;
}

public class NewBehaviourScript : MonoBehaviour
{
    string simulationURL = null;
    private float waitTime = 0.5f;
    private float timer = 0.0f;

    public GameObject prefabRobot;
    public int NumRobots;
    List<GameObject> listaRobots;

    public GameObject prefabCaja;
    public int NumCaja;
    List<GameObject> listaCaja;

    public GameObject prefabStack;
    public int NumStacks;
    List<GameObject> listaStacks;

    public GameObject prefabCajas5;
    List<GameObject> listaPrefabCajas5;

    
    Dictionary<string, int> stacks = new Dictionary<string, int>();
    Dictionary<string, int> dirty = new Dictionary<string, int>();

    // Start is called before the first frame update

    void Start()
    {
        listaRobots = new List<GameObject>();
        for (int i = 0; i < NumRobots; i++)
        {
            listaRobots.Add(Instantiate(prefabRobot, new Vector3(0.1f, 5f, 0.1f), Quaternion.identity));
        }

        listaCaja = new List<GameObject>();
        for (int i = 0; i < NumCaja; i++)
        {
            listaCaja.Add(Instantiate(prefabCaja, new Vector3(0.02f, 0f, 0.02f), Quaternion.identity));
        }

        listaStacks = new List<GameObject>();
        listaPrefabCajas5 = new List<GameObject>();
        for (int i = 0; i < NumStacks; i++)
        {
            listaStacks.Add(Instantiate(prefabStack, new Vector3(0.02f, 0f, 0.02f), Quaternion.identity));            
        }

        StartCoroutine(ConnectToMesa());
    }

    IEnumerator ConnectToMesa()
    {
        WWWForm form = new WWWForm();

        using (UnityWebRequest www = UnityWebRequest.Post("http://localhost:5000/mesa", form))
        {
            yield return www.SendWebRequest();

         
            simulationURL = www.GetResponseHeader("Location");
            Debug.Log("Connected to simulation through Web API");
            Debug.Log(simulationURL);
            
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

                //Debug.Log(www.downloadHandler.text);
                Debug.Log("Data has been processed");
                Agent[] agents = JsonHelper.FromJson<Agent>(www.downloadHandler.text);
                int i = 0;
                int j = 0;
                int k = 0;
                foreach (Agent agent in agents)
                {
                    //Debug.Log(agent);
                    if (agent.tipo == "Robot")
                    {
                        listaRobots[i].transform.position = new Vector3(agent.x, 0.1f, agent.y);
                        
                        i++;
                    }
                    else if (agent.tipo == "Caja")
                    {
                    
                        if ( (agent.limpio == true) && (agent.stackAsignadoX != -1) && (agent.stackAsignadoY != -1 ))
                        {
                            listaCaja[j].transform.position = new Vector3(agent.stackAsignadoX, .3f * agent.inStack, agent.stackAsignadoY);
                            

                        }
                        else
                        {
                            listaCaja[j].transform.position = new Vector3(agent.x, 0.3f, agent.y);

                        }
                        j++;
                    }
                    else if (agent.tipo == "Stack")
                    {
                        
                        listaStacks[k].transform.position = new Vector3(agent.x, 1.5f, .65f + agent.y);
                        k++;
                    }
                }
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
