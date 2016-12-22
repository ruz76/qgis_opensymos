<?xml version="1.0" encoding="ISO-8859-1"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:math="http://exslt.org/math" extension-element-prefixes="math">
<xsl:output method="text"/>
<xsl:template match="/">
   <xsl:for-each select="//table[@class='list']/tr">
    <!--<xsl:if test="td[1] != ''">  
        <xsl:text>&#xa;</xsl:text>
        <xsl:value-of select="td[1]"/><xsl:text>;</xsl:text>	
    </xsl:if>
    -->
    <xsl:if test="td[2]/a/@href != ''">  
        <xsl:text>&#xa;</xsl:text>
        <!--<xsl:variable name="newname">
        <xsl:call-template name="string-replace-all">
            <xsl:with-param name="text" select="td[2]" />
            <xsl:with-param name="replace" select=";" />
            <xsl:with-param name="by" select=" " />
        </xsl:call-template>
        </xsl:variable>
        -->
        <xsl:value-of select="translate(td[2],';',' ')"/><xsl:text>;</xsl:text>	
        <xsl:value-of select="substring-after(td[2]/a/@href, 'id=')"/><xsl:text>;</xsl:text>	
    </xsl:if>
    <xsl:if test="td[3] != ''">  
        <xsl:value-of select="td[3]"/><xsl:text>;</xsl:text>	
    </xsl:if>
    <xsl:if test="td[4] != ''">  
        <xsl:value-of select="td[4]"/><xsl:text>;</xsl:text>	
    </xsl:if>    
   </xsl:for-each>
   <xsl:text>&#xa;</xsl:text>
</xsl:template>

<xsl:template name="string-replace-all">
    <xsl:param name="text" />
    <xsl:param name="replace" />
    <xsl:param name="by" />
    <xsl:choose>
        <xsl:when test="$text = '' or $replace = ''or not($replace)" >
            <!-- Prevent this routine from hanging -->
            <xsl:value-of select="$text" />
        </xsl:when>
        <xsl:when test="contains($text, $replace)">
            <xsl:value-of select="substring-before($text,$replace)" />
            <xsl:value-of select="$by" />
            <xsl:call-template name="string-replace-all">
                <xsl:with-param name="text" select="substring-after($text,$replace)" />
                <xsl:with-param name="replace" select="$replace" />
                <xsl:with-param name="by" select="$by" />
            </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
            <xsl:value-of select="$text" />
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>

</xsl:stylesheet>
