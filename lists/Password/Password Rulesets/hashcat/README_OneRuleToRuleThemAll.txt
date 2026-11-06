Consulta los resultados comparativos con otros conjuntos de reglas aquí: https://www.notsosecure.com/one-rule-to-rule-them-all/
Descarga una copia actualizada aquí: https://github.com/NotSoSecure/password_cracking_rules

Hashcat se invocó de la siguiente manera:
hashcat64.exe -m0 B:\Leaks\lifeboat-raw B:\Dictionaries\rockyou.txt --status -w34 --debug-mode=1 --debug-file=stats-lifeboat-best64 -o lifeboat-best64 --potfile-disable -r rules\best64.rule

Deberías poder invocar hashcat con la opción -r para especificar la regla OneRuleToRuleThemAll.rule
