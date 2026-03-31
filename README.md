
This project is an AI-based grid game where a Trainer (Ash) tries to catch Pikachu, and Pikachu intelligently escapes using Artificial Intelligence algorithms.





The system combines:
A* → for accurate shortest path calculation
Minimax → for decision-making against an opponent
👉 The goal is to simulate a pursuit vs evasion scenario where Pikachu predicts the trainer’s moves and chooses the safest path.






🎮 Features
🟡 Intelligent Pikachu (AI-based movement)
🔴 Trainer actively chasing Pikachu
🧱 Grid-based environment with obstacles
🧠 Minimax decision-making
📍 A* pathfinding for real distance calculation
🎲 Random tie-breaking for unpredictable behavior










⚙️ Algorithms Used
🔹 A* Algorithm
Used to calculate the shortest path between trainer and Pikachu
Uses:
g(n) → distance traveled
h(n) → Manhattan distance heuristic
👉 Ensures movement respects obstacles
🔹 Minimax Algorithm
Pikachu → Maximizing player
Trainer → Minimizing player
👉 Pikachu predicts future moves and selects the best escape strategy
🔹 Integration (Key Idea 🔥)
Minimax uses A* as the evaluation function.
Leaf nodes → evaluated using A*
Decision → chosen using Minimax









![PHOTO-2026-03-28-19-20-01 2](https://github.com/user-attachments/assets/8cf83a17-09a9-43e1-a7ff-4af8fa91a0e2)

![PHOTO-2026-03-28-19-20-01 3](https://github.com/user-attachments/assets/736a372e-79dc-4d15-8040-89a1a0f71701)

![PHOTO-2026-03-28-19-20-01](https://github.com/user-attachments/assets/83f5ead1-ff65-4b27-bd33-784909b5e594)



