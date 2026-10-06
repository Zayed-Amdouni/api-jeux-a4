# 1. Fusionner les pull requests par squash

- **Date** : 2026-10-06
- **Statut** : Proposée

## Contexte

Le dépôt a reçu trois pull requests en deux séances : #7 (statistiques sur un
catalogue vide), #9 (parsing des origines autorisées) et #10 (README). Chacune
porte deux à trois commits de travail — le test qui reproduit le bug, puis la
correction, parfois un commit de mise à jour de la branche.

GitHub propose trois méthodes de fusion, et son bouton vert propose « Create a
merge commit » par défaut. Sans décision écrite, la méthode dépend de qui
clique : #7 et #9 ont été fusionnées en squash, #10 l'a été en merge commit,
par inadvertance. `main` porte donc un historique incohérent, avec un commit
`Merge branch 'main' into docs/readme` qui n'apprend rien à personne et un
commit de fusion qui double la ligne utile.

L'équipe compte trois personnes, et toute modification de `main` passe par une
pull request relue. La question n'est pas esthétique : c'est `git log main` qui
sert à répondre à « qu'est-ce qui a changé, et qui l'a validé ? ».

## Options envisagées

1. **Create a merge commit.** Pour : l'historique complet est conservé, chaque
   commit de travail garde sa date et son auteur. Contre : `main` reçoit les
   commits intermédiaires — un `wip`, un `fix typo`, un commit de fusion de
   branche — et son journal cesse d'être lisible. C'est exactement ce qui est
   arrivé avec #10.

2. **Rebase and merge.** Pour : historique linéaire, sans commit de fusion.
   Contre : exige des commits déjà propres, puisqu'ils arrivent tous tels quels
   sur `main` ; et la réécriture des SHA casse l'ancrage des commentaires de
   relecture, ce que notre workflow interdit pendant une relecture.

3. **Squash and merge.** Pour : un commit sur `main` par pull request relue,
   donc un journal où chaque ligne correspond à un changement discuté et
   approuvé ; le titre de la PR devient le message, ce qui oblige à le soigner.
   Contre : le détail des commits de la branche disparaît de `main`.

## Décision

Nous fusionnons les pull requests en **squash**. Un commit sur `main` égale une
pull request relue.

Le message du commit est le titre de la PR, au format Conventional Commits,
suivi du numéro de la PR — par exemple :

    fix(jeux): renvoyer des statistiques à zéro sur un catalogue vide (#7)

La branche est supprimée après la fusion.

## Conséquences

- `git log main` se lit comme la liste des changements relus : une ligne par
  pull request, sans bruit intermédiaire.
- **Le détail des commits de la branche disparaît de `main`.** Sur #7,
  l'historique montrait le test committé avant la correction — c'était la
  preuve que le bug avait bien été reproduit d'abord. Cette trace ne survit que
  dans la pull request, pas dans `main`.
- **`git branch -d` refuse de supprimer une branche fusionnée en squash** :
  Git ne retrouve pas ses commits dans `main`, et répond « not fully merged ».
  Il faut `-D`, donc supprimer sans filet de sécurité. Vérifier que la PR est
  bien fusionnée avant de taper la commande.
- Le titre de la pull request devient un livrable : un titre bâclé devient un
  commit bâclé, définitivement.
- **À revoir si** une pull request devient assez grosse pour que ses commits
  intermédiaires aient une valeur propre — une migration en plusieurs étapes,
  par exemple, où l'on veut pouvoir revenir à une étape intermédiaire. Dans ce
  cas, découper en plusieurs pull requests reste préférable à changer de
  méthode de fusion.
