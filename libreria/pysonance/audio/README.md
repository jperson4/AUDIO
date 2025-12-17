Intentaremos usar patchbays de pipewire (yo seguramente use helvum o carla) para conectar los inputs y los outputs de las señales

el objetovo será crear modulos que encapsulen las señales y mandar las entradas de los modulos a las entradas de las señales y las salidas de las señales a las salidas de los modulos

https://superuser.com/questions/1675877/how-to-create-a-new-pipewire-virtual-device-that-to-combines-an-real-input-and-o

ejemplos de comandos a usar:

mic:
```pactl load-module module-null-sink media.class=Audio/Source/Virtual sink_name=my-virtualmic channel_map=front-left,front-right```

```pactl load-module module-null-sink media.class=Audio/Sink sink_name=my-combined-sink channel_map=stereo```