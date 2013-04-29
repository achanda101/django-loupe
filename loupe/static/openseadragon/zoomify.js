(function( $ ){

/**
 * A client implementation of the Zoomify Format
 *
 * @class
 * @extends OpenSeadragon.TileSource
 * @param {Number|Object} width - the pixel width of the image or the idiomatic
 *      options object which is used instead of positional arguments.
 * @param {Number} height
 * @param {Number} tileSize
 * @param {String} tilesUrl
 */
$.ZoomifyTileSource = function( width, height, tileSize, tilesUrl ) {
    var options;

    if( $.isPlainObject( width ) ){
        options = width;
    }else{
        options = {
            width: arguments[0],
            height: arguments[1],
            tileSize: arguments[2],
            tilesUrl: arguments[3]
        };
    }
    if( !options.width || !options.height || !options.tilesUrl ){
        throw new Error('width, height, and tilesUrl parameters are required.');
    }
    if( !options.tileSize ){
        options.tileSize = 256;
    }

    // Initialization stuff
    var imageSize = new $.Point(options.width, options.height);
    var tiles = new $.Point(
        Math.ceil(options.width / options.tileSize),
        Math.ceil(options.height / options.tileSize)
    );

    // Create an arrays showing tier dimensions (in pixels and tiles)
    // A tier is essentially a zoom level
    this.tierSizeInTiles = [tiles];
    this.tierImageSize = [imageSize];

    while (imageSize.x > options.tileSize ||
           imageSize.y > options.tileSize ) {

        imageSize = new $.Point(
            Math.floor( imageSize.x / 2 ),
            Math.floor( imageSize.y / 2 )
            );
        tiles = new $.Point(
            Math.ceil( imageSize.x / options.tileSize ),
            Math.ceil( imageSize.y / options.tileSize )
            );
        this.tierSizeInTiles.push( tiles );
        this.tierImageSize.push( imageSize );
    }
    this.tierSizeInTiles.reverse();
    this.tierImageSize.reverse();
    this.numberOfTiers = this.tierSizeInTiles.length;
    options.maxLevel = this.numberOfTiers;
    // In order to calculate the TileGroup, we need to have an index of the
    // number of tiles in each tier
    this.tileCountUpToTier = [0];
    for (var i = 1; i < this.numberOfTiers; i++) {
        this.tileCountUpToTier.push(
            this.tierSizeInTiles[i-1].x * this.tierSizeInTiles[i-1].y +
            this.tileCountUpToTier[i-1]
            );
    }
    $.TileSource.apply( this, [ options ] );
};

$.extend( $.ZoomifyTileSource.prototype, $.TileSource.prototype, {


    /**
     * Determine if the data and/or url imply the image service is supported by
     * this tile source.
     * @function
     * @name OpenSeadragon.ZoomifyTileSource.prototype.supports
     * @param {Object|Array} data
     * @param {String} optional - url
     */
    supports: function( data, url ){
        return (
            data.type &&
            "zoomify" == data.type
        ) || (
            data.documentElement &&
            "IMAGE_PROPERTIES" == data.documentElement.tagName
        );
    },

    /**
     *
     * @function
     * @name OpenSeadragon.ZoomifyTileSource.prototype.configure
     * @param {Object|XMLDocument} data - the raw configuration
     * @param {String} url - the url the data was retreived from if any.
     * @return {Object} options - A dictionary of keyword arguments sufficient
     *      to configure this tile source via it's constructor.
     */
    configure: function( data, url ){
        if( !$.isPlainObject(data) ){
            options = configureFromXml( this, data );
        } else {
            options = configureFromObject( this, data );
        }
        var tilesurl = url || data.tilesUrl;
        service = tilesurl.split('/');
        service.pop(); //ImageProperties.json or ImageProperties.xml, or "" if slash-terminated
        service = service.join('/') + "/";
        if( 'http' !== tilesurl.substring( 0, 4 ) ){
            host = location.protocol + '//' + location.host;
            service = host + service;
        }
        options.tilesUrl = service;

        return options;
    },

    /**
     * Responsible for retreiving the url which will return an image for the
     * region speified by the given x, y, and level components.
     * @function
     * @name OpenSeadragon.ZoomifyTileSource.prototype.getTileUrl
     * @param {Number} level - z index
     * @param {Number} x
     * @param {Number} y
     * @throws {Error}
     */
    getTileUrl: function( level, x, y ){
        level = Math.max(0, level - 1);
        var tileIndex = x + y * this.tierSizeInTiles[level].x + this.tileCountUpToTier[level];
        var tileGroup = Math.floor( (tileIndex) / 256 );
        var urlstring = "TileGroup" + tileGroup + "/" + level + "-" + x + "-" + y + ".jpg";
        return options.tilesUrl + urlstring;
    }
});

/**
 * @private
 * @inner
 * @function
 *
    <IMAGE_PROPERTIES WIDTH="5569" HEIGHT="7938" NUMTILES="945" NUMIMAGES="1" VERSION="1.8" TILESIZE="256"/>
 */
function configureFromXML( tileSource, xmlDoc ){

    //parse the xml
    if ( !xmlDoc || !xmlDoc.documentElement ) {
        throw new Error( $.getString( "Errors.Xml" ) );
    }

    var root            = xmlDoc.documentElement,
        rootName        = root.tagName,
        configuration   = null;

    if ( rootName == "IMAGE_PROPERTIES" ) {
        try {
            configuration = {
                "width": root.getAttribute("WIDTH"),
                "height": root.getAttribute("HEIGHT"),
                "tileSize": root.getAttribute("TILESIZE")
            };

            return configureFromObject( tileSource, configuration );

        } catch ( e ) {
            throw (e instanceof Error) ?
                e :
                new Error( $.getString("Errors.Zoomify") );
        }
    }

    throw new Error( $.getString( "Errors.Zoomify" ) );

}

/**
 * @private
 * @inner
 * @function
 *
    {
        "width" : 6000,
        "height" : 4000,
        "tileSize" : 256
    }
 */
function configureFromObject( tileSource, configuration ){
    return configuration;
}

}( OpenSeadragon ));