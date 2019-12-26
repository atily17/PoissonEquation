# Overview
This program is Poisson's Equation solver for my study.
There is the detail explanation on [Qiita](https://qiita.com/atily17/items/ce3127bb71dcac7b5aab) (Japanese only).

It solve 2-d Poisson's Equation as follows by Finite Difference Method (FDM).

<img src="https://latex.codecogs.com/gif.latex?\inline&space;\frac{\partial^2u}{dx^2}+\frac{\partial^2u}{dy^2}=f" />

In future, It will be able to use Finite Element Method (FEM), Boundary Element Method (BEM) and so on in.

# Specification

You can use this program by setting a question.
To set the question, you can refer to json file in `Example` directory like following.

```json:Problem1
{
  "domain": {
    "shape": "Polygon",
    "vertexes": [
      [ -1, -1 ],
      [ 1, -1 ],
      [ 0.4, 1 ],
      [ -0.4, 1 ]
    ],
    "bc": {
      "bc": [
        {
          "bctype": "Dirichlet",
          "constant": -1
        },
        {
          "bctype": "Neumann",
          "constant": 0
        },
        {
          "bctype": "Dirichlet",
          "constant": 1
        },
        {
          "bctype": "Neumann",
          "constant": 0
        }
      ],
      "priority": [ 0, 2, 1, 3 ]
    }
  },
  "source": 0
}
```

- `domain`: The setting of the domain.
    - `shape`: The shape of the domain (Unfortunatly, this supports only `polygon`).
    - `vertexes`: The vertexes of polygon. If there are crossings, errors are returned.
    - `bc`: Boundaly Condition
        - `bc`: The list of setting of each border. This is the same number as vertexes.
            - `bctype`: `Direchlet` or `Neumann`
            - `constant`: The right-hand side of boundary condition. This supports only a constant function.
        - `priority`: Priority boundary at vertexes of the boundary condition.
- `source`: The source term, which is f of above equation. This supports function type (for example, `lambda x: (np.sin(x[0]))*(np.sin(x[1]))`). However, because a json file cannot read function type, it write on PoissonEquation.py like problem["source"] = *function*.

# Example

### Trapezoid
![image](./Example/ResultImage/Trapezoid(Potential).png)

![image](./Example/ResultImage/Trapezoid(FluxDensity).png)

### U-turn
![image](./Example/ResultImage/U-turn(Potential).png)

![image](./Example/ResultImage/U-turn(FluxDensity).png)

### Source on Center
![image](./Example/ResultImage/CenterSource(Potential).png)

![image](./Example/ResultImage/CenterSource(FluxDensity).png)