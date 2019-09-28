for i in $(seq 1 200);
do
    echo "$i train session"
    python trainer.py
done

