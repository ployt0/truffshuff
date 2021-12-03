This was supposed to be something simple to help me calculate what weights I 
needed and what I could do with what I already had.

After spending far too long exercising the CLI (front end) to this backend
with unit tests, winter arrived and brought the bugs that accompany the
coldest season. I lost interest.

Rather than devise the algorithm that so inspired me to create this project,
and so allow myself to use some web framework to provide a valuable service,
I'm making this project public.

I had intended to do this all along but I can now appreciate how novel
the algorithm would have to be. I could sort the weights into a stack and use
the heaviest first on the barbell, but then what happens when I want to take
the weights in a different order? Even if I instead took the bars in a 
different order I would need to identify the configurations where one bar
takes a non-contiguous range of sorted weights.

At this point my mind began to boggle. I need to further constrain my CLI,
but having satisfied myself of its functionality with unit tests that
would both involve and undo a lot of work. What constraints should I place
on the input parameters? I don't feel qualified to answer by myself.
In the interests of shelving this project I would propose the simplifications:

1. Allowing only 1 barbell (who can furnish multiple of these?)
2. Limit dumbbells to 1 to 3 pairs
3. Accept weights only as pairs
4. Don't attempt to balance an individual from a pair of weights with one
   or more from other pairs.

This takes away a good deal of the fun and experimentation from creating a
home gym. For me at least, someone incapable of solving the more generalised
version of this problem, it is a trivial problem to do manually. Considering
the effort I've put into getting this far, I'm sure it would take
disproportionately for me to arrive at a solution that merely answers the
question for me, "do I need that pair of dumbbells?". While I've been
writing this several pairs have appeared on gumtree at affordable prices.

But I still need work so I'm putting this out there as evidence of some
recent development and so I can concentrate on lower hanging fruit.

Probably I will leave this "truffshuff" alone, clone it and start again,
one day.
