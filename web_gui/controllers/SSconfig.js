// GET - config
module.exports.SSconfigView = (req, res) => {

    res.render('config/view', {title: 'Smart Speaker GUI', page: 'configView'})
}


// POST - config
module.exports.SSconfigPost= (req, res) => {

    res.redirect('/')
}