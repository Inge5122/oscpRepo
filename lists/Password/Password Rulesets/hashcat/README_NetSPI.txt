¿Qué hago con estos archivos?

OCLHashcat es compatible con estos archivos de máscaras (masks). Simplemente utiliza la opción de modo de ataque 3 (fuerza bruta) y proporciona la lista de máscaras a utilizar mediante un archivo de texto.

./oclHashcat64.bin -m 1000 hashes.txt -o output.txt -a 3 2015-Top40-Time-Sort.hcmask

¿Cuándo debería utilizarlos?

Personalmente, los utilizaría después de haber probado con algunos diccionarios y reglas. Dado que este es un ataque de fuerza bruta (en un espacio de claves limitado), no siempre es tan eficiente como los ataques basados en diccionarios y reglas. Sin embargo, he comprobado que funciona bien para contraseñas que no utilizan palabras de diccionario. Por ejemplo, un diccionario y una regla detectarían Spring15, pero sería menos probable que detectaran Gralwu94. En cambio, Gralwu94 sí sería detectada por un ataque de máscara en esta situación.

¿Cuánto tiempo tomaría esto?

Depende. Disponemos de un par de equipos con GPU dedicados a cracking entre los que podemos distribuir la carga, pero si solo lo ejecutáramos en nuestro sistema principal de cracking, tardaría alrededor de tres días y medio en completarse. Es bastante tiempo. Hay algunas máscaras peculiares en la lista que fueron fáciles de descifrar con listas de palabras y reglas (lo que generó muchos aciertos por máscara), pero toman mucho tiempo al aplicar fuerza bruta sobre el espacio de claves (?u?l?l?l?l?l?l?l?l?l?d?d – Springtime15). Revisé y registré el tiempo de cada una de las 40 principales y creé una lista ordenada por tiempo que puedes dejar de usar cuando comiences a alcanzar tus propios límites de tiempo.
