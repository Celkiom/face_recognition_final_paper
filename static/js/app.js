const linkTags = document.querySelectorAll('.navBtn')

linkTags.forEach(link => {
    link.addEventListener('click', function (){
        console.log('clicked')
    })
})

