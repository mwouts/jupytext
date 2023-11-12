# -*- coding: utf-8 -*-
# ---
# jupyter:
#   kernelspec:
#     display_name: Julia 1.1.1
#     language: julia
#     name: julia-1.1
# ---

# %%
# This notebook is a semi top-down explanation. This cell needs to be
# executed first so that the operators and helper functions are defined
# All of this is explained in the later half of the notebook

using Compose, Interact
Compose.set_default_graphic_size(2inch, 2inch)

points_f = [
    (.1, .1),
    (.9, .1),
    (.9, .2),
    (.2, .2),
    (.2, .4),
    (.6, .4),
    (.6, .5),
    (.2, .5),
    (.2, .9),
    (.1, .9),
    (.1, .1)
]

f = compose(context(), stroke("black"), line(points_f))

rot(pic) = compose(context(rotation=Rotation(-deg2rad(90))), pic)
flip(pic) = compose(context(mirror=Mirror(deg2rad(90), 0.5w, 0.5h)), pic)
above(m, n, p, q) =
    compose(context(),
            (context(0, 0, 1, m/(m+n)), p),
            (context(0, m/(m+n), 1, n/(m+n)), q))

above(p, q) = above(1, 1, p, q)

beside(m, n, p, q) =
    compose(context(),
            (context(0, 0, m/(m+n), 1), p),
            (context(m/(m+n), 0, n/(m+n), 1), q))

beside(p, q) = beside(1, 1, p, q)

over(p, q) = compose(context(),
                (context(), p), (context(), q))

rot45(pic) =
    compose(context(0, 0, 1/sqrt(2), 1/sqrt(2),
        rotation=Rotation(-deg2rad(45), 0w, 0h)), pic)

# Utility function to zoom out and look at the context
zoomout(pic) = compose(context(),
                (context(0.2, 0.2, 0.6, 0.6), pic),
                (context(0.2, 0.2, 0.6, 0.6), fill(nothing), stroke("black"), strokedash([0.5mm, 0.5mm]),
                    polygon([(0, 0), (1, 0), (1, 1), (0, 1)])))

function read_path(p_str)
    tokens = [try parsefloat(x) catch symbol(x) end for x in split(p_str, r"[\s,]+")]
    path(tokens)
end

fish = compose(context(units=UnitBox(260, 260)), stroke("black"),
            read_path(strip(readall("fish.path"))))

rotatable(pic) = @manipulate for θ=0:0.001:2π
    compose(context(rotation=Rotation(θ)), pic)
end

blank = compose(context())

fliprot45(pic) = rot45(compose(context(mirror=Mirror(deg2rad(-45))),pic))

# Hide this cell.
display(MIME("text/html"), """<script>
var cell = \$(".container .cell").eq(0), ia = cell.find(".input_area")
if (cell.find(".toggle-button").length == 0) {
ia.after(
    \$('<button class="toggle-button">Toggle hidden code</button>').click(
        function (){ ia.toggle() }
        )
    )
ia.hide()
}
</script>""")

# %% [markdown]
# # Functional Geometry
# *Functional Geometry* is a paper by Peter Henderson ([original (1982)](users.ecs.soton.ac.uk/peter/funcgeo.pdf), [revisited (2002)](https://cs.au.dk/~hosc/local/HOSC-15-4-pp349-365.pdf)) which deconstructs the MC Escher woodcut *Square Limit*
#
# ![Square Limit](http://i.imgur.com/LjRzmNM.png)

# %% [markdown]
# > A picture is an example of a complex object that can be described in terms of its parts.
# Yet a picture needs to be rendered on a printer or a screen by a device that expects to
# be given a sequence of commands. Programming that sequence of commands directly is
# much harder than having an application generate the commands automatically from the
# simpler, denotational description.

# %% [markdown]
# A `picture` is a *denotation* of something to draw.
#
# e.g. The value of f here denotes the picture of the letter F

# %% [markdown]
# Original at http://nbviewer.jupyter.org/github/shashi/ijulia-notebooks/blob/master/funcgeo/Functional%20Geometry.ipynb

# %% [markdown]
# ## In conclusion
#
# We described Escher's *Square Limit* from the description of its smaller parts, which in turn were described in terms of their smaller parts.
#
# This seemed simple because we chose to talk in terms of an *algebra* to describe pictures. The primitives `rot`, `flip`, `fliprot45`, `above`, `beside` and `over` fit the job perfectly.
#
# We were able to describe these primitives in terms of `compose` `contexts`, which the Compose library knows how to render.
#
# Denotation can be an easy way to describe a system as well as a practical implementation method.
#
# [Abstraction barriers](https://mitpress.mit.edu/sicp/full-text/sicp/book/node29.html) are useful tools that can reduce the cognitive overhead on the programmer. It entails creating layers consisting of functions which only use functions in the same layer or layers below in their own implementation. The layers in our language were:
#
#     ------------------[ squarelimit ]------------------
#     -------------[ quartet, cycle, nonet ]-------------
#     ---[ rot, flip, fliprot45, above, beside, over ]---
#     -------[ compose, context, line, path,... ]--------
#     
# Drawing this diagram out is a useful way to begin building any library.
#
